from django.db.transaction import atomic
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from apps.tests.models import Test, TestResult
from apps.tests.serializers.test import (
    CompletionTestSerializer,
    SaveAnswerTestSerializer,
    StartTestSerializer,
    TestGETSerializer,
    TestResultGETSerializer,
    TestSerializer,
)


class TestViewSet(ModelViewSet):
    """Эндпоинты сущности test."""

    queryset = Test.objects.all()
    serializer_class = TestGETSerializer
    serializer_action_classes = {
        'list': TestGETSerializer,
        'retrieve': TestGETSerializer,
        'partial_update': TestSerializer,
        'destroy': TestSerializer,
        'create': TestSerializer,
        'update': TestSerializer,
        'start_test': StartTestSerializer,
        'save_answer': SaveAnswerTestSerializer,
        'user_test': TestResultGETSerializer,
        'end_test': CompletionTestSerializer,
    }

    def get_serializer_class(self) -> Serializer:
        return self.serializer_action_classes.get(self.action)

    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(request=StartTestSerializer, responses={200: StartTestSerializer})
    @action(
        methods=['post'], detail=False, url_path='start_test', url_name='start_test'
    )
    @atomic
    def start_test(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SaveAnswerTestSerializer, responses={200: SaveAnswerTestSerializer}
    )
    @action(
        methods=['post'], detail=False, url_path='save_answer', url_name='save_answer'
    )
    @atomic
    def save_answer(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=TestResultGETSerializer,
        responses={200: TestResultGETSerializer},
        parameters=[
            OpenApiParameter(
                name='user_id',
                required=True,
                type=int,
            ),
        ],
    )
    @action(methods=['get'], detail=True, url_path='user_test', url_name='user_test')
    def user_test(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        user_id = request.query_params.get('user_id')
        serializer = self.get_serializer(instance, context={'user_id': user_id})
        return Response(serializer.data)

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name='user_id',
                required=True,
                type=int,
            ),
        ],
    )
    @action(methods=['post'], detail=True, url_path='end_test', url_name='end_test')
    @atomic
    def end_test(self, request: Request, *args, **kwargs) -> Response:
        instance = TestResult.objects.filter(
            test_id=kwargs['pk'], user_id=request.query_params.get('user_id')
        ).first()
        if instance.status is True:
            raise ValidationError('Тест уже завершён!')
        serializer = self.get_serializer(instance, data={'status': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
