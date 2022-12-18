from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, question_id):
    return HttpResponse(f"You're looking at the question {question_id}")


def results(request, question_id):
    response = "You're looking at the results of question {id}"
    return HttpResponse(response.format(id=question_id))


def vote(request, question_id):
    return HttpResponse(f"You're voting on question {question_id}")


