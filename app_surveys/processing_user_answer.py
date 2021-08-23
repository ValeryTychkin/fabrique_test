from django.db import transaction

from app_surveys.models import Choice, Answer


class UserAnswer:
    """
    Обработка, верификация и сохранения ответа пользователя на вопрос в опросе
    """

    def __init__(self, request, question, serializer_data):
        self.request = request
        self.__processing_user()
        self.__processing_answer(question, serializer_data)
        self.__verification_data()

    def __processing_user(self):
        """
        Обработка данных о пользователе
        """
        if self.request.user.is_authenticated:
            self.user_id = self.request.user.id
            self.is_anonymous = False
            self.anon_uuid = None
        else:
            self.user_id = None
            self.is_anonymous = True
            self.anon_uuid = self.request.COOKIES.get('hashcode_id')

    def __processing_answer(self, question, serializer_data):
        """
        Обработка данных о вопросе
        """
        self.question = question
        self.choices = []
        self.is_text_answer = False
        self.text_answer = None
        if question.type.name == 'one':
            choice_id = serializer_data['choices'][0]['id']
            self.choices.append(Choice.objects.select_related('question').get(id=choice_id))
        if question.type.name == 'many':
            for choice_data in serializer_data['choices']:
                self.choices.append(Choice.objects.select_related('question').get(id=choice_data['id']))
                print('Choices: ', self.choices)
        elif question.type.name == 'text':
            self.is_text_answer = True
            self.text_answer = serializer_data['answer_text']

    def __verification_data(self):
        """
        Верификация обработанных данных
        """
        self.is_verified = True
        if self.is_anonymous and not self.request.COOKIES.get('hashcode_id'):
            self.is_verified = False
        if not self.is_text_answer:
            for choice in self.choices:
                if choice.question.id != self.question.id:
                    self.is_verified = False

    @transaction.atomic
    def save(self):
        """
        Сохранение ответа пользователя в БД
        :return: True - Данные прошли верификацию и сохранены
                 False - Данные не прошли верификацию и не сохранены
        """
        if self.is_verified:
            self.__del_previous_answer()
            self.__save_user_answer()
            self.__save_user_choices()
            return True
        else:
            return False

    def __save_user_answer(self):
        """
        Сохранение ответа пользователя (без выбранных вариантов ответа)
        """
        self.user_answer = Answer.objects.create(user_id=self.user_id,
                                                 is_anonymous=self.is_anonymous,
                                                 anon_uuid=self.anon_uuid,
                                                 question=self.question,
                                                 is_text_answer=self.is_text_answer,
                                                 text_answer=self.text_answer)

    def __del_previous_answer(self):
        """
        При повторном ответе на вопрос удаляется предыдущий ответ
        """
        previous_answer = Answer.objects.filter(user_id=self.user_id,
                                                is_anonymous=self.is_anonymous,
                                                anon_uuid=self.anon_uuid,
                                                question=self.question)
        if previous_answer.exists():
            previous_answer.all().delete()

    def __save_user_choices(self):
        """
        Сохранение выбранных вариантов ответа
        """
        if not self.is_text_answer:
            self.user_answer.choice.set(self.choices)
