from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    )
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):

        if self.action == "get":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

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
