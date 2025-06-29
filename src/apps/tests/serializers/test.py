from typing import Any

from django.db.models import F
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from apps.tests.models import AnswerOption, Question, Test, TestResult
from apps.tests.serializers.question import (
    QuestionGETSerializer,
    QuestionResultGETSerializer,
)
from apps.users.models import User, UserAnswer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={
                'count': 1,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'title': 'Мой тест',
                        'questions': [
                            {
                                'id': 1,
                                'text': 'Что такое Python?',
                                'question_type': 'single',
                                'answer_options': [
                                    {
                                        'id': 1,
                                        'text': "'Python — язык программирования'",
                                        'number': 0,
                                    },
                                    {
                                        'id': 2,
                                        'text': "'Интерпретируемый язык'",
                                        'number': 1,
                                    },
                                    {
                                        'id': 3,
                                        'text': "'Машина — это компьютер'",
                                        'number': 2,
                                    },
                                    {
                                        'id': 4,
                                        'text': "'Интерпретируемый язык'",
                                        'number': 3,
                                    },
                                ],
                            },
                            {
                                'id': 12,
                                'text': 'Выберите все правильные утверждения о воде.',
                                'question_type': 'multiple',
                                'answer_options': [
                                    {'id': 5, 'text': 'Вода — жидкость’', 'number': 0},
                                    {'id': 6, 'text': "'Вода — газ’", 'number': 1},
                                    {
                                        'id': 7,
                                        'text': '’Вода — твердый материал’',
                                        'number': 2,
                                    },
                                ],
                            },
                        ],
                    }
                ],
            },
            response_only=True,
        ),
    ]
)
class TestGETSerializer(serializers.ModelSerializer):
    questions = QuestionGETSerializer(read_only=True, many=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'questions')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={'id': 2, 'title': 'New test', 'questions': []},
            response_only=True,
        ),
        OpenApiExample(
            name='Valid example request', value={'title': 'New test'}, request_only=True
        ),
    ]
)
class TestSerializer(serializers.ModelSerializer):
    questions = QuestionGETSerializer(read_only=True, many=True)

    class Meta:
        model = Test
        fields = (
            'id',
            'title',
            'questions',
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={
                'id': 1,
                'test_id': 1,
                'user_id': 1,
                'total_questions': 10,
                'status': False,
                'results': 0,
            },
            response_only=True,
        ),
        OpenApiExample(
            name='Valid example request',
            value={
                'user_id': 1,
                'test_id': 1,
            },
            request_only=True,
        ),
    ]
)
class StartTestSerializer(serializers.ModelSerializer):
    user_id = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        source='user',
    )
    test_id = PrimaryKeyRelatedField(
        queryset=Test.objects.all(),
        required=True,
        source='test',
    )
    total_questions = serializers.IntegerField(min_value=1, read_only=True)
    status = serializers.BooleanField(read_only=True)
    results = serializers.IntegerField(read_only=True)

    class Meta:
        model = TestResult
        fields = ('id', 'user_id', 'test_id', 'total_questions', 'status', 'results')

    def create(self, validated_data: dict[str, Any]) -> TestResult:
        test = validated_data['test']
        validated_data['total_questions'] = test.questions.count()
        return super().create(validated_data)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={
                'id': 1,
                'user_id': 1,
                'question_id': 1,
                'selected_choices': [1],
            },
            response_only=True,
        ),
        OpenApiExample(
            name='Valid example request',
            value={
                'user_id': 1,
                'question_id': 1,
                'numbers': [1],
            },
            request_only=True,
        ),
    ]
)
class SaveAnswerTestSerializer(serializers.ModelSerializer):
    user_id = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        source='user',
    )
    question_id = PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
        required=True,
        source='question',
    )
    numbers = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        write_only=True,
    )
    selected_choices = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = UserAnswer
        fields = (
            'id',
            'user_id',
            'question_id',
            'numbers',
            'selected_choices',
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user = attrs['user']
        question = attrs['question']
        test = question.test
        answer_numbers = attrs['numbers']

        if not TestResult.objects.filter(user=user, test=test).exists():
            raise ValidationError('Пользователь не начал этот тест.')

        valid_numbers = set(
            AnswerOption.objects.filter(question_id=question.id).values_list(
                'number', flat=True
            )
        )
        if not set(answer_numbers).issubset(valid_numbers):
            raise ValidationError('Некорректные номера ответов.')

        return attrs

    def create(self, validated_data: dict[str, Any]) -> UserAnswer:
        question = validated_data['question']
        user = validated_data['user']
        answer_numbers = validated_data['numbers']

        answer_options = AnswerOption.objects.filter(
            question=question, number__in=answer_numbers
        ).values('id', 'is_correct')

        if all(answer_option['is_correct'] for answer_option in answer_options):
            TestResult.objects.filter(user=user, test=question.test).update(
                results=F('results') + 1
            )

        user_answer = UserAnswer.objects.create(
            user=user,
            question=question,
        )
        user_answer.selected_choices.set(
            [answer_option['id'] for answer_option in answer_options]
        )
        return user_answer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example response',
            value={
                'count': 1,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'title': 'Мой тест',
                        'questions': [
                            {
                                'id': 1,
                                'text': 'Что такое Python?',
                                'question_type': 'single',
                                'answer_options': [
                                    {
                                        'id': 1,
                                        'text': "'Python — язык программирования'",
                                        'number': 0,
                                    },
                                    {
                                        'id': 2,
                                        'text': "'Интерпретируемый язык'",
                                        'number': 1,
                                    },
                                    {
                                        'id': 3,
                                        'text': "'Машина — это компьютер'",
                                        'number': 2,
                                    },
                                    {
                                        'id': 4,
                                        'text': "'Интерпретируемый язык'",
                                        'number': 3,
                                    },
                                ],
                                'selected_choices': [{'id': 1, 'number': 0}],
                            },
                            {
                                'id': 12,
                                'text': 'Выберите все правильные утверждения о воде.',
                                'question_type': 'multiple',
                                'answer_options': [
                                    {'id': 5, 'text': 'Вода — жидкость’', 'number': 0},
                                    {'id': 6, 'text': "'Вода — газ’", 'number': 1},
                                    {
                                        'id': 7,
                                        'text': '’Вода — твердый материал’',
                                        'number': 2,
                                    },
                                ],
                                'selected_choices': [
                                    {'id': 5, 'number': 0},
                                    {'id': 6, 'number': 1},
                                ],
                            },
                        ],
                    }
                ],
            },
            response_only=True,
        ),
    ]
)
class TestResultGETSerializer(serializers.ModelSerializer):
    questions = QuestionResultGETSerializer(read_only=True, many=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'questions')


class CompletionTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('id', 'status', 'results', 'total_questions')
