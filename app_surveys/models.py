from django.conf import settings
from django.db import models
from django.urls import reverse


class Survey(models.Model):
    """
    Опрос
        name: Название
        date_start: Дата старта
        date_end: Дата окончания
        description: Описание опроса
    """

    name = models.CharField(max_length=300)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=2000)

    @property
    def api_href(self):
        """
        :return: Ссылка на первый вопрос в данном опросе
        """
        return f"{reverse('survey')}?survey_id={self.id}"

    def __str__(self):
        return f'{self.id}: {self.name}'


class AnswerType(models.Model):
    """
    Тип ответа на вопрос
        name: Название
            'one'-> Один вариант выбора
            'many'-> Несколько вариантов выбора
            'text'-> Ответ текстом
    """
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Вопрос
        survey: Опрос (какого опроса данный вопрос) Survey OneToOne
        type: Тип (какой тип ответа на данный вопрос) AnswerType OneToOne
        text: Текст (сам вопрос)
    """

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    type = models.ForeignKey(AnswerType, on_delete=models.CASCADE)
    text = models.CharField(max_length=1500)

    @property
    def questions_num(self):
        """
        :return: Общее кол. вопросов в данном опросе
        """
        return Question.objects.filter(survey=self.survey).count()

    @property
    def question_num(self):
        """
        :return: Порядковый номер вопроса в данном опросе
        """
        questions_id_list = list(Question.objects.values_list('id', flat=True)
                                 .filter(survey=self.survey)
                                 .order_by('id'))
        return questions_id_list.index(self.id) + 1

    @property
    def next(self):
        """
        :return: URL на следующий вопрос (если таковой имеется)
        """
        if self.question_num < self.questions_num:
            return f"{reverse('survey')}?survey_id={self.survey.id}&question={self.question_num + 1}"

    @property
    def previous(self):
        """
        :return: URL на предыдущий вопрос (если таковой имеется)
        """
        if self.question_num != 1:
            return f"{reverse('survey')}?survey_id={self.survey.id}&question={self.question_num - 1}"

    def __str__(self):
        return self.text


class Choice(models.Model):
    """
    Вариант ответа
        question: Вопрос (какого вопроса данный вариант) Question OneToOne
        title: Текст (сам вариант)
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    title = models.CharField(max_length=150)

    def __str__(self):
        return f'question {self.question}: {self.title}'


class Answer(models.Model):
    """
    Ответ на вопрос
        user: ID аутентифицированного пользователя (NULL если анон.)
        is_anonymous: Является ли пользователем анон. (True если анон.)
        anon_uuid: UUID анон. (NULL если не анон.)
        question: Вопрос (на какой вопрос данный ответ) Question OneToOne
        choice: Выбранный вариант ответа (NULL если ответ текстом) Choice ManyToMany
        is_text_answer: Является ли ответ текстом (False если не является)
        text_answer: Текстовый ответ пользователя (NULL если это вопрос с вариантами ответа)
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    anon_uuid = models.CharField(max_length=32, null=True, blank=True, default=None)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ManyToManyField(Choice, blank=True, default=None)
    is_text_answer = models.BooleanField(default=False)
    text_answer = models.CharField(max_length=1000, null=True, blank=True, default=None)

    def __str__(self):
        if not self.is_anonymous:
            return f'{self.id}: user_id {self.user.id}'
        else:
            return f'{self.id}: anonymous_uuid {self.anon_uuid}'

