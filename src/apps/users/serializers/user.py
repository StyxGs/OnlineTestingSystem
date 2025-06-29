from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework.serializers import ModelSerializer

from apps.users.models import User


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={
                'id': 1,
                'first_name': 'first_name',
                'last_name': 'last_name',
            },
            response_only=True,
        ),
        OpenApiExample(
            name='Valid example request',
            value={
                'first_name': 'first_name',
                'last_name': 'last_name',
            },
            request_only=True,
        ),
    ]
)
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
        )
