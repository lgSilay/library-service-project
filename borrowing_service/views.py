from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import status

from borrowing_service.models import Borrowing
from borrowing_service.serializers.common import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from payments_service.utils import create_stripe_session


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
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

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

        is_active = self.request.query_params.get("is_active")
        if is_active:
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
        return Response(
            {"session_url": session_url},
            status=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    @action(
        methods=["GET"],
        detail=True,
        url_path="return_borrowing",
        permission_classes=[IsAuthenticated],
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        actual_date_today = {"actual_return_date": timezone.now().date()}
        serializer = self.get_serializer(borrowing, data=actual_date_today)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
