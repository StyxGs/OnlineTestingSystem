from django.core.validators import MaxValueValidator
from django.db import models


class Test(models.Model):
    title = models.CharField(max_length=128, unique=True)


class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
    )
    test = models.ForeignKey(
        'tests.Test', related_name='questions', on_delete=models.CASCADE
    )
    text = models.CharField(max_length=256)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)


class AnswerOption(models.Model):
    question = models.ForeignKey(
        'tests.Question', related_name='answer_options', on_delete=models.CASCADE
    )
    text = models.CharField(max_length=256)
    number = models.PositiveIntegerField()
    is_correct = models.BooleanField(default=False)


class TestResult(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
    )
    test = models.ForeignKey(
        'tests.Test',
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(default=False)
    results = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(1),
        ]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=[
                    'user',
                    'test',
                ],
                name='unique_user_and_test',
            ),
        )
