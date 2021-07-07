from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.http import Http404
from datetime import date
import json

from .models import Poll, Submission, Answer
from .serializers import PollSerializer, QuestionSerializer, \
    UserOptionSerializer, SubmissionSerializer


class Polls(APIView):
    def get(self, request):
        today = date.today()
        poll_set = Poll.objects.filter(start_date__lte=today,
                                       finish_date__gt=today)
        return Response(PollSerializer(poll_set, many=True).data)


class PollById(APIView):
    def get(self, request, id):
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.start_date > today or poll.finish_date < today:
                raise Poll.DoesNotExist()

            result = PollSerializer(poll).data
            result['questions'] = []
            for question in poll.question_set.all():
                question_dict = QuestionSerializer(question).data
                if question.hasOptionType:
                    question_dict['options'] = UserOptionSerializer(
                        question.option_set.all(), many=True).data
                result['questions'].append(question_dict)

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def post(self, request, id):
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.start_date > today or poll.finish_date < today:
                raise Poll.DoesNotExist()

            if not 'userId' in request.data:
                raise Exception('userId is missing')
            if not type(request.data['userId']) is int:
                raise Exception('Invalid userId')
            if not 'answers' in request.data:
                raise Exception('answers are missing')
            if not type(request.data['answers']) is dict:
                raise Exception('Invalid answers')

            user_id = request.data['userId']
            answer_dict = request.data['answers']

            if Submission.objects.filter(userId=user_id,
                                         poll=poll).count() > 0:
                raise Exception('This user already has submitted to this poll')

            def makeAnswer(question):
                if not str(question.id) in answer_dict:
                    raise Exception(
                        'Answer to question %d is missing' % question.id)

                answer_data = answer_dict[str(question.id)]
                answer = Answer(
                    question=question,
                    questionType=question.type,
                    questionText=question.text)

                invalidAnswerException = Exception(
                    'Invalid answer to question %d' % question.id
                )
                invalidIndexException = Exception(
                    'Invalid option index in answer to question %d'
                    % question.id
                )
                if question.type == 'TEXT':
                    if not type(answer-data) is str:
                        raise invalidAnswerException
                    answer.answer_text = answer_data

                if question.type == 'CHOICE':
                    if not type(answer_data) is int:
                        raise invalidAnswerException
                    found_option = question.option_set.filter(
                        index=answer_data).first()
                    if found_option:
                        answer.answer_text = found_option.text
                    else:
                        raise invalidIndexException

                if question.type == 'MULTIPLE_CHOICE':
                    if not type(answer_data) is list:
                        raise invalidAnswerException
                    option_list = question.option_set.all()
                    result_list = []
                    for index in answer_data:
                        found_option = next(
                            (o for o in option_list if o.index == index), None)
                        if found_option:
                            resultList.append(found_option.text)
                        else:
                            raise invalidIndexException
                    answer.answer_text = json.dumps(result_list)

                return answer

            answer_list = [make_answer(question) for question in
                          poll.question_set.all()]
            if len(answer_list) != poll.question_set.count():
                raise Exception('Not enough answers')

            submis = Submission(user_id=user_id, poll=poll)
            submis.save()
            for answer in answer_list:
                answer.submission = submis
                answer.save()

            return Response('Accepted')

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class PollsByUser(APIView):
    def get(self, request, id):
        try:
            result = []
            for submission in Submission.objects.filter(user_id=id).order_by(
                    'submitTime'):
                submission_dict = SubmissionSerializer(submission).data
                submission_dict['pollId'] = submission.poll_id
                submission_dict['answers'] = []
                for answer in submission.answer_set.all():
                    answer_text = answer.answer_text
                    if answer.question_type == 'MULTIPLE_CHOICE':
                        answer_text = json.loads(answer_text)

                    submission_dict['answers'].append({
                        'question': {
                            'id': answer.question_id,
                            'type': answer.question_type,
                            'text': answer.question_text
                        },
                        'answer': answer_text
                    })

                result.append(submission_dict)

            return Response(result)

        except Exception as ex:
            raise ParseError(ex)
