from rest_framework import serializers

from app_surveys.models import Survey, Question, Choice


class SurveysListSerializer(serializers.ModelSerializer):
    survey_id = serializers.IntegerField(source='id')
    survey_name = serializers.CharField(source='name')
    survey_description = serializers.CharField(source='description')
    survey_href = serializers.CharField(source='api_href')

    class Meta:
        model = Survey
        fields = ['survey_id',
                  'survey_name',
                  'survey_description',
                  'survey_href']
        read_only_fields = fields


class ChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Choice
        fields = ['id', 'title']


class QuestionSerializer(serializers.ModelSerializer):
    question_type = serializers.CharField(source='type.name')
    choices = ChoiceSerializer(many=True, allow_null=True)

    class Meta:
        model = Question
        fields = ['id',
                  'questions_num',
                  'next',
                  'previous',
                  'text',
                  'question_type',
                  'choices']
        read_only_fields = fields


class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choices = ChoiceSerializer(many=True, allow_null=True)
    answer_text = serializers.CharField(allow_blank=True, allow_null=True, default=None)
