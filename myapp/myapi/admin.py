from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.exceptions import ParseError
from django.http import Http404
from datetime import date

from .models import Poll, Question, Option, validateQuestionType
from .serializers import PollSerializer, QuestionSerializer, OptionSerializer


class AdminAPIView(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]


class AdminPolls(AdminAPIView):
    def get(self, request):
        return Response(PollSerializer(Poll.objects.all(), many=True).data)

    def post(self, request):
        try:
            s = PollSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            if d['start_date'] > d['finish_date']:
                raise Exception('Invalid finish_date')

            new_poll = Poll(**d)
            new_poll.save()
            return Response(PollSerializer(new_poll).data)
        except Exception as ex:
            raise ParseError(ex)


class AdminPollById(AdminAPIView):
    def get(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            result = PollSerializer(poll).data
            result['questions'] = []
            for question in poll.question_set.all():
                question_dict = QuestionSerializer(question).data
                if question.hasOptionType:
                    questionDict['options'] = OptionSerializer(
                        question.option_set.all(), many=True).data
                result['questions'].append(questionDict)

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def delete(self, request, id):
        try:
            Poll.objects.get(id=id).delete()
            return Response('Deleted')
        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def patch(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            d = request.data
            if 'name' in d:
                poll.name = d['name']
            if 'description' in d:
                poll.description = d['description']
            if 'finishDate' in d:
                poll.finishDate = date.fromisoformat(d['finishDate'])

            if poll.start_date > poll.finish_date:
                raise Exception('Invalid finishDate')

            poll.save()
            return Response(PollSerializer(poll).data)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class AdminQuestions(AdminAPIView):
    def post(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            qs = QuestionSerializer(data=request.data)
            qs.is_valid(raise_exception=True)
            pd = dict(qs.validated_data)
            pd['poll'] = poll
            new_question = Question(**pd)

            require_options = new_question.hasOptionType
            new_option_list = []
            if requireOptions:
                if not 'options' in request.data:
                    raise Exception('options are missing')
                if type(request.data['options']) != list or len(
                        request.data['options']) < 2:
                    raise Exception('Invalid options')

                index = 1
                for option_text in request.data['options']:
                    new_option_list.append(Option(
                        text=option_text,
                        index=index
                    ))
                    index += 1

            newQuestion.save()
            if require_options:
                for new_option in new_option_list:
                    new_option.question = new_question
                    new_option.save()

            result = QuestionSerializer(new_question).data
            if require_options:
                result['options'] = [OptionSerializer(o).data for o in
                                     new_option_list]

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class AdminQuestionById(AdminAPIView):
    def get(self, request, pollId, questionId):
        try:
            question = Question.objects.get(id=questionId)
            result = QuestionSerializer(question).data
            if question.hasOptionType:
                result['options'] = OptionSerializer(question.option_set.all(),
                                                     many=True)
            return Response(result)

        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def delete(self, request, pollId, questionId):
        try:
            Question.objects.get(id=questionId).delete()
            return Response('Deleted')
        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def patch(self, request, pollId, questionId):
        try:
            deleteExistingOptions = False
            requireNewOptions = False
            prevQuestion = Question.objects.get(id=questionId)
            nextQuestion = Question.objects.get(id=questionId)
            d = request.data
            if 'text' in d:
                nextQuestion.text = d['text']
            if 'type' in d:
                validateQuestionType(d['type'])
                nextQuestion.type = d['type']

            if prevQuestion.hasOptionType and not nextQuestion.hasOptionType:
                deleteExistingOptions = True
            if not prevQuestion.hasOptionType and nextQuestion.hasOptionType:
                requireNewOptions = True
            if prevQuestion.hasOptionType and nextQuestion.hasOptionType and 'options' in d:
                deleteExistingOptions = requireNewOptions = True

            if requireNewOptions:
                if not 'options' in d:
                    raise Exception('options are missing')
                if type(d['options']) != list or len(d['options']) < 2:
                    raise Exception('Invalid options')

            if deleteExistingOptions:
                Option.objects.filter(question=nextQuestion).delete()

            if requireNewOptions:
                index = 1
                for optionText in d['options']:
                    Option(text=optionText, index=index,
                           question=nextQuestion).save()
                    index += 1

            nextQuestion.save()

            result = QuestionSerializer(nextQuestion).data
            if nextQuestion.hasOptionType:
                result['options'] = OptionSerializer(
                    nextQuestion.option_set.all(), many=True).data

            return Response(result)

        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)
