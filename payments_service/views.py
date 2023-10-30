import logging

from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework_simplejwt.views import status
import stripe
from borrowing_service.tasks import send_notification_task

from payments_service.models import Payment
from payments_service.serializers.common import (
    PaymentListSerializer,
    PaymentDetailSerializer,
)
from payments_service.permissions import IsOwnerOrAdmin
from payments_service.utils import create_stripe_session


logger = logging.getLogger("payments_service")


class RenewPaymentSessionView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if payment.status == "expired":
            borrowing = payment.borrowing
            session = create_stripe_session(
                request, borrowing, payment.money_to_pay
            )
            payment.session_url = session.url
            payment.session_id = session.id
            payment.status = "pending"
            payment.save()
            return Response(
                {"session_url": session.url},
                status=status.HTTP_307_TEMPORARY_REDIRECT,
            )
        return Response(
            {"info": "This payment is not expired"}, status=status.HTTP_200_OK
        )


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Payment.objects.select_related("borrowing__book")
    serializer_class = PaymentDetailSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return self.serializer_class

    @action(methods=["GET"], detail=False, url_path="success")
    def order_success(self, request):
        if session_id := request.query_params.get("session_id"):
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(session_id=session_id)
            if session["payment_status"] == "paid":
                payment.status = "paid"
                payment.save()
                message = (
                    f"{payment.money_to_pay}$ for "
                    f"{payment.borrowing} were paid"
                )
                send_notification_task.delay(message)
                logger.info(f"Successful payment {payment.id}")
                return Response(
                    {"info": "Your payment was successful"},
                    status=status.HTTP_200_OK,
                )
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="cancel")
    def order_cancel(self, request):
        logger.info(f"Delayed payment")
        return Response(
            {
                "info": (
                    "Payment can be performed a bit later. "
                    "Session will be active for 24 hours."
                )
            },
            status=status.HTTP_200_OK,
        )
