# Generated by Django 2.2.10 on 2021-08-23 21:06

from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import migrations


SURVEYS_NUM = 2


def add_data(apps, schema_editor):
    create_superuser(apps, schema_editor)
    add_answer_types(apps, schema_editor)
    add_survey_date_none(apps, schema_editor)
    add_questions(apps, schema_editor)
    update_survey_days_today(apps, schema_editor)


def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.create(username='admin',
                        password=make_password('admin'),
                        is_staff=True,
                        is_active=True,
                        is_superuser=True)


def add_answer_types(apps, schema_editor):
    AnswerType = apps.get_model('app_surveys', 'AnswerType')
    answer_types_names = ['one',
                          'many',
                          'text']

    for answer_type_name in answer_types_names:
        AnswerType.objects.create(name=answer_type_name)


def add_survey_date_none(apps, schema_editor):
    Survey = apps.get_model('app_surveys', 'Survey')
    for survey_counter in range(SURVEYS_NUM):
        Survey.objects.create(name='Test',
                              description='Test, test test test')


def add_questions(apps, schema_editor):
    Survey = apps.get_model('app_surveys', 'Survey')
    Question = apps.get_model('app_surveys', 'Question')
    AnswerType = apps.get_model('app_surveys', 'AnswerType')
    Choice = apps.get_model('app_surveys', 'Choice')
    choices_num = 3

    for survey_obj in Survey.objects.all():
        for answer_type_obj in AnswerType.objects.all():
            question_obj = Question.objects.create(survey=survey_obj,
                                                   type=answer_type_obj,
                                                   text=f'test_{survey_obj.id}_{answer_type_obj.name}')
            if answer_type_obj.name == 'one' or answer_type_obj.name == 'many':
                for choice_num in range(choices_num):
                    Choice.objects.create(question=question_obj,
                                          title=f'test_{question_obj.survey.id}_choice_{choice_num}')


def update_survey_days_today(apps, schema_editor):
    Survey = apps.get_model('app_surveys', 'Survey')
    Survey.objects.all().update(date_start=date.today(),
                                date_end=date.today())


class Migration(migrations.Migration):
    dependencies = [
        ('app_surveys', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]
