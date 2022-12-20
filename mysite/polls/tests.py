from django.test import TestCase

# Create your tests here.
from .models import Question
from django.utils import timezone
from django.urls import reverse

import datetime


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for question whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days, choice_text=None):
    """
    Create a question with the given `question_text` and pulished the
    given number of `days` offset to now(negative for questions
    published in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if choice_text:
        # check the question for a choice_text
        question.choice_set.create(choice_text=choice_text, votes=0)
        return question
    else:
        return question


class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [], )

    def test_past_question_choices(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        Question in the past with a choice.
        """
        question = create_question(question_text="Past question.", days=-30, choice_text='Past')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_past_question_no_choices(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        Question in the past with no choice.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question_choices(self):
        """
        Even if both past and future questions exist, only past questions are displayed.
        Two questions, one in the future, one in the past with a choice.
        """
        question = create_question(question_text="Past question.", days=-30, choice_text='Past')
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question_and_past_question_no_choices(self):
        """
        Even if both past and future questions exist, only past questions are displayed.
        Two questions, one in the future, one in the past with no choice.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [],
        )

    def test_two_past_questions_two_choices(self):
        """
        The questions index page may display multiple questions.
        Two questions in the past with a choice.
        """
        question1 = create_question(question_text="Past question 1.", days=-30, choice_text='Past1')
        question2 = create_question(question_text="Past question 2.", days=-5, choice_text='Past2')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

    def test_two_past_questions_one_choices(self):
        """
        The questions index page may display multiple questions.
        Two questions in the past, one with a choice.
        """
        question1 = create_question(question_text="Past question 1.", days=-30, choice_text='Past1')
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question1],
        )

    def test_two_past_questions_no_choices(self):
        """
        The questions index page may display multiple questions.
        Two question in the past with no choice.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [],
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question_choices(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found.
        Question in the future with a choice.
        """
        future_question = create_question(question_text='Future question.', days=5, choice_text='Future')
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_no_choices(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found.
        Question in the future with no choice.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_choices(self):
        """
        The detail view of a question with a pub_date in the past displays the question's text.
        Question in the past with a choice.
        """
        past_question = create_question(question_text='Past question.', days=-5, choice_text='Past')
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choices(self):
        """
        The detail view of a question with a pub_date in the past displays the question's text.
        Question in the past with no choice.
        """
        past_question = create_question(question_text='Past question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultsViewTests(TestCase):
    def test_future_question_no_choices(self):
        """
        The results view of a question with a pub_date in the future returns a 404 not found.
        Question in the future with no choice.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_choices(self):
        """
        The results view of a question with a pub_date in the future returns a 404 not found.
        Question in the future with a choice.
        """
        future_question = create_question(question_text='Future question.', days=5, choice_text='Future')
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_no_choices(self):
        """
        The results view of a question with a pub_date in the past displays the question's text.
        Question in the past with no choice.
        """
        past_question = create_question(question_text='Past question.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_choices(self):
        """
        The results view of a question with a pub_date in the past displays the question's text.
        Question in the past with a choice.
        """
        past_question = create_question(question_text='Past question.', days=-5, choice_text='Past')
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
