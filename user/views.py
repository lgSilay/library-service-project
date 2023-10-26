from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from user.serializers import UserSerializer, TelegramUserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class TelegramUserView(
    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    queryset = get_user_model().objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
