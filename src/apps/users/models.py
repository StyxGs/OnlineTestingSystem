from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)


class UserAnswer(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    question = models.ForeignKey('tests.Question', on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(
        'tests.AnswerOption', related_name='user_answers'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=[
                    'user',
                    'question',
                ],
                name='unique_user_and_question',
            ),
        )
