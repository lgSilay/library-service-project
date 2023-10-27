import logging

from django.utils import timezone
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import settings
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from borrowing_service.models import Borrowing
from borrowing_service.permissions import IsOwnerOrAdmin
from borrowing_service.serializers.common import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from payments_service.utils import create_stripe_session


logger = logging.getLogger("borrowing_service")


class ReturnBorrowingView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def post(self, request: Request, pk: int) -> Response:
        borrowing = get_object_or_404(Borrowing, pk=pk)
        self.check_object_permissions(request, borrowing)

        actual_return_date = timezone.now().date()
        data = {"actual_return_date": actual_return_date}
        serializer = BorrowingReturnSerializer(borrowing, data=data)

        if serializer.is_valid():
            serializer.save()
            borrowing.refresh_from_db()
            if actual_return_date > borrowing.expected_return_date:
                money_to_pay = (
                    (actual_return_date - borrowing.expected_return_date).days
                    * borrowing.book.daily_fee
                    * settings.FINE_MULTIPLIER
                )
                session_url = create_stripe_session(
                    request, borrowing, money_to_pay, type="fine"
                )
                return Response(
                    {"session_url": session_url}, status=status.HTTP_200_OK
                )
            logger.info("Returned borrowing successful", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book").prefetch_related(
        "payments"
    )
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return self.serializer_class

    @staticmethod
    def _params_to_ints(params):
        """Convert a list of string ids to a list of integers"""
        return [int(str_id) for str_id in params.split(",")]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                int_user_id = self._params_to_ints(user_id)
                queryset = queryset.filter(user_id__in=int_user_id)
        else:
            queryset = queryset.filter(user=user)

        if "is_active" in self.request.query_params:
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save(user=request.user)
        money_to_pay = (
            borrowing.expected_return_date - borrowing.borrow_date
        ).days * borrowing.book.daily_fee
        session_url = create_stripe_session(request, borrowing, money_to_pay)
        logger.info(
            "Created borrowing successful, expect payment",
            serializer.data
        )
        return Response(
            {"session_url": session_url},
            status=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type={"type": "str"},
                description="Filter to see the "
                "unreturned borrowing (ex. ?is_active)",
            ),
            OpenApiParameter(
                "user_id",
                type={"type": "list", "items": {"type": "number"}},
                description="Only for staff: "
                            "filter by user (ex. ?user_id=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
