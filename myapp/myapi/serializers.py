from rest_framework import serializers
from .models import Poll, Question, Option, Submission, Answer


class PollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = '__all__'


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class UserOptionSerializer(serializers.ModelSerializer):
    """User response option"""
    index = serializers.IntegerField()
    text = serializers.CharField(max_length=100)
