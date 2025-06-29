from rest_framework.serializers import ModelSerializer

from apps.tests.models import AnswerOption


class AnswerOptionGETSerializer(ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = (
            'id',
            'text',
            'number',
        )


class AnswerResultOptionGETSerializer(ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = (
            'id',
            'number',
        )
