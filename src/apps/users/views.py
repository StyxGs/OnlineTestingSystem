from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from apps.tests.models import Test
from apps.tests.serializers.test import TestGETSerializer
from apps.users.serializers.user import UserSerializer


class UserViewSet(ModelViewSet):
    """Эндпоинты сущности user."""

    queryset = Test.objects.all()
    serializer_class = TestGETSerializer
    serializer_action_classes = {
        'list': UserSerializer,
        'retrieve': UserSerializer,
        'partial_update': UserSerializer,
        'destroy': UserSerializer,
        'create': UserSerializer,
        'update': UserSerializer,
    }

    def get_serializer_class(self) -> Serializer:
        return self.serializer_action_classes.get(self.action)

    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)
