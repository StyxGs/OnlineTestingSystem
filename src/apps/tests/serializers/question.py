from rest_framework import serializers

from apps.tests.models import Question
from apps.tests.serializers.answer import (
    AnswerOptionGETSerializer,
    AnswerResultOptionGETSerializer,
)
from apps.users.models import UserAnswer


class QuestionGETSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionGETSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'text',
            'question_type',
            'answer_options',
        )


class QuestionResultGETSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionGETSerializer(read_only=True, many=True)
    selected_choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'answer_options', 'selected_choices')

    def get_selected_choices(self, obj: Question):
        user_id = self.context.get('user_id')
        if not user_id:
            return []

        try:
            user_answer = UserAnswer.objects.get(user_id=user_id, question=obj)
        except UserAnswer.DoesNotExist:
            return []

        selected = user_answer.selected_choices.all()
        serializer = AnswerResultOptionGETSerializer(selected, many=True)
        return serializer.data
