import pandas as pd
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from apps.tests.models import AnswerOption, Question, Test


class Command(BaseCommand):
    help = 'Импорт данных из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    @atomic
    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        df = pd.read_csv(csv_file_path)

        df['test_title'] = df['test_title'].ffill()

        unique_tests = df['test_title'].unique()

        tests_objs = [Test(title=title) for title in unique_tests]
        created_tests = Test.objects.bulk_create(
            tests_objs,
            update_conflicts=True,
            update_fields=['title'],
            unique_fields=['title'],
        )
        tests_map = {test.title: test for test in created_tests}

        grouped = df.groupby('test_title')

        questions_list = []
        questions_info = []
        for test_title, group in grouped:
            test_obj = tests_map[test_title]
            for _, row in group.iterrows():
                questions_list.append(
                    Question(
                        test=test_obj,
                        text=row['question_text'],
                        question_type=row['question_type'],
                    )
                )
                questions_info.append(
                    {
                        'question_text': row['question_text'],
                        'test_title': test_title,
                        'choices': [c.strip() for c in row['choices'].split(',')],
                        'correct_answers': {
                            int(n.strip()) for n in row['correct_answers'].split(',')
                        },
                    }
                )

        questions_in_db = Question.objects.bulk_create(questions_list)

        questions_map = {(q.test.title, q.text): q for q in questions_in_db}

        answers_data = []
        for info in questions_info:
            question_obj = questions_map[(info['test_title'], info['question_text'])]
            choices = info['choices']
            correct_indices = info['correct_answers']
            answers_data.extend(
                [
                    AnswerOption(
                        question=question_obj,
                        number=index,
                        text=choices[index],
                        is_correct=(index in correct_indices),
                    )
                    for index in range(len(choices))
                ]
            )

        AnswerOption.objects.bulk_create(answers_data)

        self.stdout.write(self.style.SUCCESS('Тесты успешно импортированы'))
