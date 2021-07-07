from django.contrib import admin
from django.urls import path, include

from .admin import AdminPolls, AdminPollById, \
    AdminQuestions, AdminQuestionById
from .views import Polls, PollById, PollsByUser

urlpatterns = [
    path('polls', Polls.as_view()),
    path('polls/<int:id>', PollById.as_view()),
    path('pollsByUser/<int:id>', PollsByUser.as_view()),
    path('admin/', include([
        path('polls', AdminPolls.as_view()),
        path('polls/<int:id>', AdminPollById.as_view()),
        path('polls/<int:id>/questions', AdminQuestions.as_view()),
        path('polls/<int:pollId>/questions/<int:questionId>',
             AdminQuestionById.as_view())
    ]))
]
