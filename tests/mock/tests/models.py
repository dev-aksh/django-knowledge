from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from mock.tests.base import TestCase
from knowledge.models import Question, Response


class BasicModelTest(TestCase):
    def test_basic_question_answering(self):
        """
        Given a question asked by a real user, track answering and accepted states.
        """

        ## joe asks a question ##
        question = Question.objects.create(
            user = self.joe,
            title = 'What time is it?',
            body = 'Whenever I look at my watch I see the little hand at 3 and the big hand at 7.'
        )

        self.assertFalse(question.answered())
        self.assertFalse(question.accepted())

        # passes quietly
        question.accept()

        ## admin responds ##
        response = Response.objects.create(
            question = question,
            user = self.admin,
            body = 'The little hand at 3 means 3 pm or am, the big hand at 7 means 3:35 am or pm.'
        )

        self.assertTrue(question.answered())
        self.assertFalse(question.accepted())


        ## joe accepts the answer ##
        question.accept(response)

        self.assertTrue(question.answered())
        self.assertTrue(question.accepted())


    def test_switching_question(self):
        ## joe asks a question ##
        question = self.question
        self.assertEquals(question.status, 'private')

        question.public()
        self.assertEquals(question.status, 'public')

        question.internal()
        self.assertEquals(question.status, 'internal')

        question.private()
        self.assertEquals(question.status, 'private')

        # no change
        question.inherit()
        self.assertEquals(question.status, 'private')


    def test_switching_response(self):
        ## joe asks a question ##
        response = self.response
        self.assertEquals(response.status, 'inherit')

        response.public()
        self.assertEquals(response.status, 'public')

        response.internal()
        self.assertEquals(response.status, 'internal')

        response.private()
        self.assertEquals(response.status, 'private')

        response.inherit()
        self.assertEquals(response.status, 'inherit')


    def test_private_states(self):
        """
        Walk through the public, private and internal states for Question, and public, private,
        inherit and internal states for Response.

        Then checks who can see what with .can_view(<User>).
        """

        ## joe asks a question ##
        question = self.question

        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and publicizes this question ##
        question.public()

        # everyone can see
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and internalizes this question ##
        question.internal()

        # only admin can see
        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))
        self.assertFalse(question.can_view(self.joe))

        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and privatizes this question ##
        question.private()
        
        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## admin responds ##
        response = self.response
        response.inherit()

        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))

        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone comes along and publicizes the parent question ##
        question.public()

        self.assertTrue(response.can_view(self.anon))
        self.assertTrue(response.can_view(self.bob))
        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone privatizes the response ##
        response.private()

        # everyone can see question still
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))
        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))

        # only joe and admin can see the response though
        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))

        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone internalizes the response ##
        response.internal()

        # everyone can see question still
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))
        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))

        # only admin can see the response though
        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))
        self.assertFalse(response.can_view(self.joe))

        self.assertTrue(response.can_view(self.admin))

    
    def test_url(self):
        self.assertEquals(
            '/knowledge/questions/{0}/{1}/'.format(
                self.question.id,
                slugify(self.question.title)),
            self.question.get_absolute_url()
        )


    def test_normal_question(self):
        self.assertEquals(self.question.get_name(), 'Joe Dirt')
        self.assertEquals(self.question.get_email(), 'joedirt@example.com')


    def test_anon_question(self):
        q = Question.objects.create(
            title = 'Where is my cat?',
            body = 'His name is whiskers.',
            name = 'Joe Dirt',
            email = 'joedirt@example.com'
        )

        self.assertEquals(q.get_name(), 'Joe Dirt')
        self.assertEquals(q.get_email(), 'joedirt@example.com')























