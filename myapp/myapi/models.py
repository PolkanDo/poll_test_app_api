from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


def validateQuestionType(value):
    if not value in ['TEXT', 'CHOICE', 'MULTIPLE_CHOICE']:
        raise ValidationError('Invalid question type')


OPTION_TYPES = ['CHOICE', 'MULTIPLE_CHOICE']


class Poll(models.Model):
    """Poll class"""
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    start_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField()
    description = models.CharField(max_length=300)

    class Meta:
        verbose_name = _("Poll")
        verbose_name_plural = _("Polls")
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question class"""
    text = models.CharField(max_length=255, verbose_name=_("Question"))
    type = models.CharField(max_length=30, validators=[validateQuestionType])
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)

    @property
    def hasOptionType(self):
        return self.type in OPTION_TYPES

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["id"]

    def __str__(self):
        return self.text


class Option(models.Model):
    """Possible answer"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    text = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Option")
        verbose_name_plural = _("Options")

    def __str__(self):
        return self.text


class Submission(models.Model):
    """Completed Poll"""
    user_id = models.IntegerField(db_index=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    submit_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")

    def __str__(self):
        user = self.user['id']
        poll = self.poll['title']
        submit_time = self.submit_time
        return f"User {user} finished {poll} poll at {submit_time}."


class Answer(models.Model):
    """Answer for question"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=30,
                                     validators=[validateQuestionType])
    question_text = models.CharField(max_length=300)
    answer_text = models.CharField(max_length=300)

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __str__(self):
        question_text = self.question["text"]
        question_type = self.question["type"]
        answer_text = self.answer_text
        return f"Question type: \n{question_type}; " \
               f"\nQuestion: {question_text}." \
               f"\nAnswer: {answer_text}."
