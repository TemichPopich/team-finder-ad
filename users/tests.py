from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Skill

User = get_user_model()

# Common test data constants
TEST_PASSWORD = 'testpass123'
TEST_SURNAME = 'User'

# Skill test data
SKILL_PYTHON = 'Python'
SKILL_JAVASCRIPT = 'JavaScript'
SKILL_DJANGO = 'Django'

# URL constants
URL_LOGIN = 'users:login'
URL_REGISTER = 'users:register'
URL_PARTICIPANTS = 'users:participants'
URL_PROJECT_LIST = 'projects:project_list'

# Template constants
TEMPLATE_REGISTER = 'users/register.html'
TEMPLATE_LOGIN = 'users/login.html'
TEMPLATE_PARTICIPANTS = 'users/participants.html'

# Form field constants
FORM_FIELD_NAME = 'name'
FORM_FIELD_SURNAME = 'surname'
FORM_FIELD_EMAIL = 'email'
FORM_FIELD_PASSWORD1 = 'password1'
FORM_FIELD_PASSWORD2 = 'password2'
FORM_FIELD_USERNAME = 'username'
FORM_FIELD_PASSWORD = 'password'

# Error messages
ERROR_INVALID_EMAIL = 'Enter a valid email address'


class UserModelTest(TestCase):
    """Tests for the custom User model."""

    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test')
        self.assertEqual(user.surname, TEST_SURNAME)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin',
            surname=TEST_SURNAME,
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='str@example.com',
            name='John',
            surname='Doe',
            password=TEST_PASSWORD
        )
        self.assertEqual(str(user), 'John Doe')


class SkillModelTest(TestCase):
    """Tests for the Skill model."""

    def test_create_skill(self):
        """Test creating a skill."""
        skill = Skill.objects.create(name=SKILL_PYTHON)
        self.assertEqual(skill.name, SKILL_PYTHON)

    def test_skill_str_representation(self):
        """Test skill string representation."""
        skill = Skill.objects.create(name=SKILL_JAVASCRIPT)
        self.assertEqual(str(skill), SKILL_JAVASCRIPT)

    def test_skill_ordering(self):
        """Test that skills are ordered by name."""
        Skill.objects.create(name=SKILL_PYTHON)
        Skill.objects.create(name=SKILL_DJANGO)
        Skill.objects.create(name=SKILL_JAVASCRIPT)

        skills = list(Skill.objects.all())
        self.assertEqual(skills[0].name, SKILL_DJANGO)
        self.assertEqual(skills[1].name, SKILL_JAVASCRIPT)
        self.assertEqual(skills[2].name, SKILL_PYTHON)


class UserSkillTest(TestCase):
    """Tests for user skills relationship."""

    def test_add_skill_to_user(self):
        """Test adding skills to a user."""
        user = User.objects.create_user(
            email='skills@example.com',
            name='Skill',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        skill1 = Skill.objects.create(name=SKILL_PYTHON)
        skill2 = Skill.objects.create(name=SKILL_DJANGO)

        user.skills.add(skill1, skill2)

        self.assertIn(skill1, user.skills.all())
        self.assertIn(skill2, user.skills.all())
        self.assertEqual(user.skills.count(), 2)

    def test_remove_skill_from_user(self):
        """Test removing a skill from a user."""
        user = User.objects.create_user(
            email='remove@example.com',
            name='Remove',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        skill = Skill.objects.create(name=SKILL_PYTHON)
        user.skills.add(skill)

        user.skills.remove(skill)

        self.assertNotIn(skill, user.skills.all())
        self.assertEqual(user.skills.count(), 0)


class RegisterViewTest(TestCase):
    """Tests for the registration view."""

    def test_register_get(self):
        """Test registration page GET request."""
        response = self.client.get(reverse(URL_REGISTER))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_REGISTER)

    def test_register_post_valid(self):
        """Test registration with valid data."""
        response = self.client.post(reverse(URL_REGISTER), {
            FORM_FIELD_NAME: 'Test',
            FORM_FIELD_SURNAME: TEST_SURNAME,
            FORM_FIELD_EMAIL: 'test@example.com',
            FORM_FIELD_PASSWORD1: TEST_PASSWORD,
            FORM_FIELD_PASSWORD2: TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse(URL_PROJECT_LIST))
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_register_post_invalid(self):
        """Test registration with invalid data."""
        response = self.client.post(reverse(URL_REGISTER), {
            FORM_FIELD_NAME: 'Test',
            FORM_FIELD_SURNAME: TEST_SURNAME,
            FORM_FIELD_EMAIL: 'invalid-email',
            FORM_FIELD_PASSWORD1: TEST_PASSWORD,
            FORM_FIELD_PASSWORD2: TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_REGISTER)
        self.assertContains(response, ERROR_INVALID_EMAIL)


class LoginViewTest(TestCase):
    """Tests for the login view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='login@example.com',
            name='Login',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )

    def test_login_get(self):
        """Test login page GET request."""
        response = self.client.get(reverse(URL_LOGIN))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_LOGIN)

    def test_login_post_valid(self):
        """Test login with valid credentials."""
        response = self.client.post(reverse(URL_LOGIN), {
            FORM_FIELD_USERNAME: 'login@example.com',
            FORM_FIELD_PASSWORD: TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse(URL_PROJECT_LIST))

    def test_login_post_invalid(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse(URL_LOGIN), {
            FORM_FIELD_USERNAME: 'login@example.com',
            FORM_FIELD_PASSWORD: 'wrongpassword',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_LOGIN)


class ParticipantsViewTest(TestCase):
    """Tests for the participants list view."""

    def setUp(self):
        self.skill1 = Skill.objects.create(name=SKILL_PYTHON)
        self.skill2 = Skill.objects.create(name=SKILL_JAVASCRIPT)
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            name='User',
            surname='One',
            password=TEST_PASSWORD
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            name='User',
            surname='Two',
            password=TEST_PASSWORD
        )
        self.user1.skills.add(self.skill1)
        self.user2.skills.add(self.skill2)

    def test_participants_list(self):
        """Test participants list without filter."""
        response = self.client.get(reverse(URL_PARTICIPANTS))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_PARTICIPANTS)
        self.assertEqual(len(response.context['participants']), 2)

    def test_participants_filter_by_skill(self):
        """Test filtering participants by skill."""
        response = self.client.get(reverse(URL_PARTICIPANTS), {'skill': SKILL_PYTHON})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['participants']), 1)
        participants_list = list(response.context['participants'])
        self.assertEqual(participants_list[0].email, 'user1@example.com')
