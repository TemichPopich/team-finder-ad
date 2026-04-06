from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Project

User = get_user_model()

# Common test data constants
TEST_PASSWORD = 'testpass123'
TEST_SURNAME = 'User'
TEST_PROJECT_STATUS_OPEN = 'open'
TEST_PROJECT_STATUS_CLOSED = 'closed'

# User test data - emails
USER_OWNER_EMAIL = 'owner@example.com'
USER_OWNER_NAME = 'Project'

USER_LIST_EMAIL = 'list@example.com'
USER_LIST_NAME = 'List'

USER_DETAILS_EMAIL = 'details@example.com'
USER_DETAILS_NAME = 'Details'

USER_CREATE_EMAIL = 'create@example.com'
USER_CREATE_NAME = 'Create'

USER_EDIT_EMAIL = 'edit@example.com'
USER_EDIT_NAME = 'Edit'

USER_OTHER_EMAIL = 'other@example.com'
USER_OTHER_NAME = 'Other'

USER_COMPLETE_EMAIL = 'complete@example.com'
USER_COMPLETE_NAME = 'Complete'

USER_OTHER2_EMAIL = 'other2@example.com'
USER_OTHER2_NAME = 'Other2'

USER_PARTICIPATE_EMAIL = 'participate@example.com'
USER_PARTICIPATE_NAME = 'Participate'

USER_OWNER2_EMAIL = 'owner2@example.com'
USER_OWNER2_NAME = 'Owner'
USER_OWNER2_SURNAME = 'Two'

USER_FAVORITE_EMAIL = 'favorite@example.com'
USER_FAVORITE_NAME = 'Favorite'

USER_OWNER3_EMAIL = 'owner3@example.com'
USER_OWNER3_NAME = 'Owner'
USER_OWNER3_SURNAME = 'Three'

# Project test data
PROJECT_TEST_NAME = 'Test Project'
PROJECT_TEST_DESCRIPTION = 'Test Description'

PROJECT_MY_NAME = 'My Project'

PROJECT_AUTO_NAME = 'Auto Participant'

PROJECT_FIRST_NAME = 'First'
PROJECT_SECOND_NAME = 'Second'

PROJECT_OPEN_1_NAME = 'Open Project 1'
PROJECT_OPEN_2_NAME = 'Open Project 2'
PROJECT_CLOSED_NAME = 'Closed Project'

PROJECT_DETAIL_NAME = 'Detail Project'
PROJECT_DETAIL_DESCRIPTION = 'Project Description'

PROJECT_NEW_NAME = 'New Project'
PROJECT_NEW_DESCRIPTION = 'New Description'

PROJECT_EMPTY_NAME = ''
PROJECT_EMPTY_DESCRIPTION = 'Description'

PROJECT_EDIT_NAME = 'Edit Project'
PROJECT_EDIT_DESCRIPTION = 'Original Description'
PROJECT_UPDATED_NAME = 'Updated Project'
PROJECT_UPDATED_DESCRIPTION = 'Updated Description'

PROJECT_COMPLETE_NAME = 'Complete Project'

PROJECT_PARTICIPATE_NAME = 'Participate Project'

PROJECT_FAVORITE_NAME = 'Favorite Project'

# Form field constants
FORM_FIELD_NAME = 'name'
FORM_FIELD_DESCRIPTION = 'description'
FORM_FIELD_STATUS = 'status'

# URL constants
URL_LOGIN = 'users:login'
URL_PROJECT_LIST = 'projects:project_list'
URL_PROJECT_DETAILS = 'projects:project_details'
URL_CREATE_PROJECT = 'projects:create_project'
URL_EDIT_PROJECT = 'projects:edit_project'
URL_COMPLETE_PROJECT = 'projects:complete_project'
URL_TOGGLE_PARTICIPATE = 'projects:toggle_participate'
URL_FAVORITE_PROJECTS = 'projects:favorite_projects'

# Template constants
TEMPLATE_PROJECT_LIST = 'projects/project_list.html'
TEMPLATE_PROJECT_DETAILS = 'projects/project-details.html'
TEMPLATE_CREATE_PROJECT = 'projects/create-project.html'
TEMPLATE_FAVORITE_PROJECTS = 'projects/favorite_projects.html'

# Error messages
ERROR_PERMISSION_DENIED = 'Permission denied'
ERROR_OWNER_CANNOT_LEAVE = 'Owner cannot leave project'
ERROR_PROJECT_ALREADY_CLOSED = 'Project already closed'


class ProjectModelTest(TestCase):
    """Tests for the Project model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_OWNER_EMAIL,
            name=USER_OWNER_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )

    def test_create_project(self):
        """Test creating a project."""
        project = Project.objects.create(
            name=PROJECT_TEST_NAME,
            description=PROJECT_TEST_DESCRIPTION,
            owner=self.user
        )
        self.assertEqual(project.name, PROJECT_TEST_NAME)
        self.assertEqual(project.description, PROJECT_TEST_DESCRIPTION)
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.status, TEST_PROJECT_STATUS_OPEN)

    def test_project_str_representation(self):
        """Test project string representation."""
        project = Project.objects.create(
            name=PROJECT_MY_NAME,
            owner=self.user
        )
        self.assertEqual(str(project), PROJECT_MY_NAME)

    def test_owner_added_as_participant(self):
        """Test that owner is automatically added as participant."""
        project = Project.objects.create(
            name=PROJECT_AUTO_NAME,
            owner=self.user
        )
        self.assertIn(self.user, project.participants.all())

    def test_project_ordering(self):
        """Test that projects are ordered by created_at descending."""
        Project.objects.create(name=PROJECT_FIRST_NAME, owner=self.user)
        Project.objects.create(name=PROJECT_SECOND_NAME, owner=self.user)

        projects = list(Project.objects.all())
        self.assertEqual(projects[0].name, PROJECT_SECOND_NAME)
        self.assertEqual(projects[1].name, PROJECT_FIRST_NAME)


class ProjectListViewTest(TestCase):
    """Tests for the project list view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_LIST_EMAIL,
            name=USER_LIST_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        Project.objects.create(
            name=PROJECT_OPEN_1_NAME, owner=self.user, status=TEST_PROJECT_STATUS_OPEN)
        Project.objects.create(
            name=PROJECT_OPEN_2_NAME, owner=self.user, status=TEST_PROJECT_STATUS_OPEN)
        Project.objects.create(
            name=PROJECT_CLOSED_NAME, owner=self.user, status=TEST_PROJECT_STATUS_CLOSED)

    def test_project_list_get(self):
        """Test project list page GET request."""
        response = self.client.get(reverse(URL_PROJECT_LIST))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_PROJECT_LIST)
        self.assertEqual(len(response.context['projects']), 2)

    def test_project_list_excludes_closed(self):
        """Test that closed projects are excluded."""
        response = self.client.get(reverse(URL_PROJECT_LIST))
        projects = response.context['projects']
        for project in projects:
            self.assertEqual(project.status, TEST_PROJECT_STATUS_OPEN)


class ProjectDetailsViewTest(TestCase):
    """Tests for the project details view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_DETAILS_EMAIL,
            name=USER_DETAILS_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name=PROJECT_DETAIL_NAME,
            description=PROJECT_DETAIL_DESCRIPTION,
            owner=self.user
        )

    def test_project_details_get(self):
        """Test project details page GET request."""
        response = self.client.get(
            reverse(URL_PROJECT_DETAILS, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_PROJECT_DETAILS)
        self.assertEqual(response.context['project'], self.project)

    def test_project_details_not_found(self):
        """Test project details with non-existent ID."""
        response = self.client.get(reverse(URL_PROJECT_DETAILS, args=[999]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class CreateProjectViewTest(TestCase):
    """Tests for the create project view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_CREATE_EMAIL,
            name=USER_CREATE_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )

    def test_create_project_get_requires_login(self):
        """Test that create project requires login."""
        response = self.client.get(reverse(URL_CREATE_PROJECT))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_CREATE_PROJECT)}")

    def test_create_project_get(self):
        """Test create project page GET request for logged in user."""
        self.client.login(email=USER_CREATE_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse(URL_CREATE_PROJECT))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_CREATE_PROJECT)

    def test_create_project_post_valid(self):
        """Test creating a project with valid data."""
        self.client.login(email=USER_CREATE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_CREATE_PROJECT), {
            FORM_FIELD_NAME: PROJECT_NEW_NAME,
            FORM_FIELD_DESCRIPTION: PROJECT_NEW_DESCRIPTION,
            FORM_FIELD_STATUS: TEST_PROJECT_STATUS_OPEN,
        })
        latest_project = Project.objects.latest('id')
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[latest_project.id]))
        self.assertTrue(Project.objects.filter(name=PROJECT_NEW_NAME).exists())

    def test_create_project_post_invalid(self):
        """Test creating a project with invalid data."""
        self.client.login(email=USER_CREATE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_CREATE_PROJECT), {
            FORM_FIELD_NAME: PROJECT_EMPTY_NAME,
            FORM_FIELD_DESCRIPTION: PROJECT_EMPTY_DESCRIPTION,
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_CREATE_PROJECT)


class EditProjectViewTest(TestCase):
    """Tests for the edit project view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_EDIT_EMAIL,
            name=USER_EDIT_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.other_user = User.objects.create_user(
            email=USER_OTHER_EMAIL,
            name=USER_OTHER_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name=PROJECT_EDIT_NAME,
            description=PROJECT_EDIT_DESCRIPTION,
            owner=self.user
        )

    def test_edit_project_get_requires_login(self):
        """Test that edit project requires login."""
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_EDIT_PROJECT, args=[self.project.id])}")

    def test_edit_project_owner(self):
        """Test that owner can edit project."""
        self.client.login(email=USER_EDIT_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_project_not_owner(self):
        """Test that non-owner cannot edit project."""
        self.client.login(email=USER_OTHER_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[self.project.id]))

    def test_edit_project_post_valid(self):
        """Test editing a project with valid data."""
        self.client.login(email=USER_EDIT_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_EDIT_PROJECT, args=[self.project.id]), {
            FORM_FIELD_NAME: PROJECT_UPDATED_NAME,
            FORM_FIELD_DESCRIPTION: PROJECT_UPDATED_DESCRIPTION,
            FORM_FIELD_STATUS: TEST_PROJECT_STATUS_OPEN,
        })
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[self.project.id]))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, PROJECT_UPDATED_NAME)


class CompleteProjectViewTest(TestCase):
    """Tests for the complete project view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_COMPLETE_EMAIL,
            name=USER_COMPLETE_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.other_user = User.objects.create_user(
            email=USER_OTHER2_EMAIL,
            name=USER_OTHER2_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name=PROJECT_COMPLETE_NAME,
            owner=self.user,
            status=TEST_PROJECT_STATUS_OPEN
        )

    def test_complete_project_requires_login(self):
        """Test that completing project requires login."""
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_COMPLETE_PROJECT, args=[self.project.id])}")

    def test_complete_project_owner(self):
        """Test that owner can complete project."""
        self.client.login(email=USER_COMPLETE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, TEST_PROJECT_STATUS_CLOSED)

    def test_complete_project_not_owner(self):
        """Test that non-owner cannot complete project."""
        self.client.login(email=USER_OTHER2_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_complete_already_closed_project(self):
        """Test completing an already closed project."""
        self.project.status = TEST_PROJECT_STATUS_CLOSED
        self.project.save()
        self.client.login(email=USER_COMPLETE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class ToggleParticipateViewTest(TestCase):
    """Tests for the toggle participate view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_PARTICIPATE_EMAIL,
            name=USER_PARTICIPATE_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.owner = User.objects.create_user(
            email=USER_OWNER2_EMAIL,
            name=USER_OWNER2_NAME,
            surname=USER_OWNER2_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name=PROJECT_PARTICIPATE_NAME,
            owner=self.owner,
            status=TEST_PROJECT_STATUS_OPEN
        )

    def test_toggle_participate_requires_login(self):
        """Test that toggling participation requires login."""
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id])}")

    def test_toggle_participate_join(self):
        """Test joining a project."""
        self.client.login(email=USER_PARTICIPATE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.user, self.project.participants.all())

    def test_toggle_participate_leave(self):
        """Test leaving a project."""
        self.project.participants.add(self.user)
        self.client.login(email=USER_PARTICIPATE_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.user, self.project.participants.all())

    def test_owner_cannot_leave_project(self):
        """Test that owner cannot leave their own project."""
        self.client.login(email=USER_OWNER2_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class FavoriteProjectsViewTest(TestCase):
    """Tests for the favorite projects view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email=USER_FAVORITE_EMAIL,
            name=USER_FAVORITE_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.owner = User.objects.create_user(
            email=USER_OWNER3_EMAIL,
            name=USER_OWNER3_NAME,
            surname=USER_OWNER3_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name=PROJECT_FAVORITE_NAME,
            owner=self.owner,
            status=TEST_PROJECT_STATUS_OPEN
        )
        self.project.participants.add(self.user)

    def test_favorite_projects_requires_login(self):
        """Test that viewing favorites requires login."""
        response = self.client.get(reverse(URL_FAVORITE_PROJECTS))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_FAVORITE_PROJECTS)}")

    def test_favorite_projects_get(self):
        """Test viewing favorite projects."""
        self.client.login(email=USER_FAVORITE_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse(URL_FAVORITE_PROJECTS))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_FAVORITE_PROJECTS)
        self.assertIn(self.project, response.context['projects'])
