from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Skill

User = get_user_model()

# Common test data constants
TEST_PASSWORD = 'testpass123'
TEST_SURNAME = 'User'
TEST_ADMIN_PASSWORD = 'adminpass123'
TEST_WRONG_PASSWORD = 'wrongpassword'

# User test data - emails
USER_TEST_EMAIL = 'test@example.com'
USER_TEST_NAME = 'Test'

USER_ADMIN_EMAIL = 'admin@example.com'
USER_ADMIN_NAME = 'Admin'

USER_STR_EMAIL = 'str@example.com'
USER_STR_NAME = 'John'
USER_STR_SURNAME = 'Doe'

USER_SKILLS_EMAIL = 'skills@example.com'
USER_SKILLS_NAME = 'Skill'

USER_REMOVE_EMAIL = 'remove@example.com'
USER_REMOVE_NAME = 'Remove'

USER_REGISTER_EMAIL = 'test@example.com'
USER_REGISTER_NAME = 'Test'

USER_LOGIN_EMAIL = 'login@example.com'
USER_LOGIN_NAME = 'Login'

USER_PARTICIPANTS_1_EMAIL = 'user1@example.com'
USER_PARTICIPANTS_1_NAME = 'User'
USER_PARTICIPANTS_1_SURNAME = 'One'

USER_PARTICIPANTS_2_EMAIL = 'user2@example.com'
USER_PARTICIPANTS_2_NAME = 'User'
USER_PARTICIPANTS_2_SURNAME = 'Two'

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
            email=USER_TEST_EMAIL,
            name=USER_TEST_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.assertEqual(user.email, USER_TEST_EMAIL)
        self.assertEqual(user.name, USER_TEST_NAME)
        self.assertEqual(user.surname, TEST_SURNAME)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email=USER_ADMIN_EMAIL,
            name=USER_ADMIN_NAME,
            surname=TEST_SURNAME,
            password=TEST_ADMIN_PASSWORD
        )
        self.assertEqual(user.email, USER_ADMIN_EMAIL)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email=USER_STR_EMAIL,
            name=USER_STR_NAME,
            surname=USER_STR_SURNAME,
            password=TEST_PASSWORD
        )
        self.assertEqual(str(user), f'{USER_STR_NAME} {USER_STR_SURNAME}')


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
            email=USER_SKILLS_EMAIL,
            name=USER_SKILLS_NAME,
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
            email=USER_REMOVE_EMAIL,
            name=USER_REMOVE_NAME,
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
            FORM_FIELD_NAME: USER_REGISTER_NAME,
            FORM_FIELD_SURNAME: TEST_SURNAME,
            FORM_FIELD_EMAIL: USER_REGISTER_EMAIL,
            FORM_FIELD_PASSWORD1: TEST_PASSWORD,
            FORM_FIELD_PASSWORD2: TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse(URL_PROJECT_LIST))
        self.assertTrue(User.objects.filter(email=USER_REGISTER_EMAIL).exists())

    def test_register_post_invalid(self):
        """Test registration with invalid data."""
        response = self.client.post(reverse(URL_REGISTER), {
            FORM_FIELD_NAME: USER_REGISTER_NAME,
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
            email=USER_LOGIN_EMAIL,
            name=USER_LOGIN_NAME,
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
            FORM_FIELD_USERNAME: USER_LOGIN_EMAIL,
            FORM_FIELD_PASSWORD: TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse(URL_PROJECT_LIST))

    def test_login_post_invalid(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse(URL_LOGIN), {
            FORM_FIELD_USERNAME: USER_LOGIN_EMAIL,
            FORM_FIELD_PASSWORD: TEST_WRONG_PASSWORD,
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_LOGIN)


class ParticipantsViewTest(TestCase):
    """Tests for the participants list view."""

    def setUp(self):
        self.skill1 = Skill.objects.create(name=SKILL_PYTHON)
        self.skill2 = Skill.objects.create(name=SKILL_JAVASCRIPT)
        self.user1 = User.objects.create_user(
            email=USER_PARTICIPANTS_1_EMAIL,
            name=USER_PARTICIPANTS_1_NAME,
            surname=USER_PARTICIPANTS_1_SURNAME,
            password=TEST_PASSWORD
        )
        self.user2 = User.objects.create_user(
            email=USER_PARTICIPANTS_2_EMAIL,
            name=USER_PARTICIPANTS_2_NAME,
            surname=USER_PARTICIPANTS_2_SURNAME,
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
        self.assertEqual(participants_list[0].email, USER_PARTICIPANTS_1_EMAIL)
