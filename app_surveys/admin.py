from django.contrib import admin

from app_surveys import models as models_app


class QuestionInLine(admin.TabularInline):
    model = models_app.Question


@admin.register(models_app.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_start', 'date_end')
    inlines = [QuestionInLine]


class ChoiceInLine(admin.TabularInline):
    model = models_app.Choice


@admin.register(models_app.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'type')
    inlines = [ChoiceInLine]


@admin.register(models_app.AnswerType)
class AnswerTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
