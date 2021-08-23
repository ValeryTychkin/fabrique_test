from django.urls import path

from app_surveys.views import SurveysList, SurveyQuestion

urlpatterns = [
    path('surveys/', SurveysList.as_view(), name='surveys list'),
    path('survey/', SurveyQuestion.as_view(), name='survey'),
]