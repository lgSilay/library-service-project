from rest_framework import viewsets, mixins

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

    def get_serializer_class(self):

        if self.action == "get":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return self.serializer_class
