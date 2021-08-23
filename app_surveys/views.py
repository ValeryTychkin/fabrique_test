from datetime import date

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app_surveys.models import Survey, Question
from app_surveys.processing_user_answer import UserAnswer
from app_surveys.serializers import SurveysListSerializer, QuestionSerializer, AnswerSerializer


class SurveysListPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 30


class SurveysList(ListAPIView):
    """
    Представление для получения списка актуальных опросов
    (макс. отзывов на странице = 6)

    Сортируется по дате начала от старых к новым
    (Дата начала <= Сегодня && Дата окончания >= Сегодня)
    """

    serializer_class = SurveysListSerializer
    pagination_class = SurveysListPagination

    def get_queryset(self):
        """
        :return: Объекты модели Survey отсортированных по дате начала от старых к новым
                 фильтр: (Дата начала <= Сегодня && Дата окончания >= Сегодня)
        """
        today = date.today()
        return Survey.objects.filter(date_start__lte=today, date_end__gte=today).order_by('-date_start')

    def get(self, request, *args, **kwargs):
        """
        :return: Список актуальных опросов
        """
        return self.list(request, *args, **kwargs)


class SurveyQuestion(APIView):
    """
    Представление для получения вопроса выбранного опроса
    GET: survey_id=INT (id опроса); question=INT (порядковый номер вопроса в опросе)

    Сохранение ответа на вопрос происходит путем отправки POST запросом JSON объекта:
        {
            "question_id": INT (id вопроса),
            "answer_text": STR (Текстовый ответ NULL=True),
            "choices": [
                {
                    "id": INT (id выбранного варианта),
                    "title": STR (title выбранного варианта)
                }
            ] (many=True, NULL=True)
        }
    """

    serializer_class = QuestionSerializer
    answer_serializer_class = AnswerSerializer

    def get_queryset(self):
        """
        :return: Объект модели Question согласно GET запросу
                 Если данные не прошли верификацию, то возвращается пустой объект
        """
        today = date.today()
        return Question.objects.select_related('type', 'survey').filter(id=self.get_question_id(),
                                                                        survey__date_start__lte=today,
                                                                        survey__date_end__gte=today).first()

    def get_question_id(self):
        """
        :return: Возвращает id вопроса
                 Если данные не прошли верификацию, то возвращается 0
        """
        if self.request.query_params.get('survey_id'):
            survey_id = self.request.query_params['survey_id']
            question_num = self.get_question_num(survey_id) - 1
            questions_id = list(Question.objects.values_list('id', flat=True)
                                .filter(survey_id=survey_id)
                                .order_by('id'))
            return questions_id[question_num]
        else:
            return 0

    def get_question_num(self, survey_id):
        """
        :return: Возвращает порядковый номер вопроса
                 Если порядковый номер вопроса отправленным пользователем больше максимального или меньше 1
                     то возвращается максимальное значение или же 1
                 Если порядковый не был отправлен, то возвращается 1
        """
        if self.request.query_params.get('question'):
            question_num = int(self.request.query_params['question'])
            max_question_num = Question.objects.filter(survey_id=survey_id).order_by('id').count()
            if question_num > max_question_num:
                question_num = max_question_num
            if question_num < 1:
                question_num = 1
        else:
            question_num = 1
        return question_num

    def get(self, request):
        """
        :return: Вопрос согласно данным полученным из GET
        """
        serializer = self.serializer_class(self.get_queryset())
        return Response(serializer.data)

    def post(self, request):
        """
        Принимает JSON объект для сохранения актуального ответа пользователя отправившим POST зарос
        """
        serializer = self.answer_serializer_class(data=request.data)
        if serializer.is_valid():
            question = Question.objects.select_related('type').get(id=serializer.data['question_id'])
            if question:
                # обработка сохранение ответа пользователя путем передачи данных в класс UserAnswer
                user_answer = UserAnswer(request, question, serializer.data)
                if user_answer.save():
                    return Response(status.HTTP_200_OK)
        return Response(status.HTTP_406_NOT_ACCEPTABLE)
