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


class ProjectModelTest(TestCase):
    """Tests for the Project model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            name='Project',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )

    def test_create_project(self):
        """Test creating a project."""
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.description, 'Test Description')
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.status, TEST_PROJECT_STATUS_OPEN)

    def test_project_str_representation(self):
        """Test project string representation."""
        project = Project.objects.create(
            name='My Project',
            owner=self.user
        )
        self.assertEqual(str(project), 'My Project')

    def test_owner_added_as_participant(self):
        """Test that owner is automatically added as participant."""
        project = Project.objects.create(
            name='Auto Participant',
            owner=self.user
        )
        self.assertIn(self.user, project.participants.all())

    def test_project_ordering(self):
        """Test that projects are ordered by created_at descending."""
        Project.objects.create(name='First', owner=self.user)
        Project.objects.create(name='Second', owner=self.user)

        projects = list(Project.objects.all())
        self.assertEqual(projects[0].name, 'Second')
        self.assertEqual(projects[1].name, 'First')


class ProjectListViewTest(TestCase):
    """Tests for the project list view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='list@example.com',
            name='List',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        Project.objects.create(
            name='Open Project 1', owner=self.user, status=TEST_PROJECT_STATUS_OPEN)
        Project.objects.create(
            name='Open Project 2', owner=self.user, status=TEST_PROJECT_STATUS_OPEN)
        Project.objects.create(
            name='Closed Project', owner=self.user, status=TEST_PROJECT_STATUS_CLOSED)

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
            email='details@example.com',
            name='Details',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name='Detail Project',
            description='Project Description',
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
            email='create@example.com',
            name='Create',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )

    def test_create_project_get_requires_login(self):
        """Test that create project requires login."""
        response = self.client.get(reverse(URL_CREATE_PROJECT))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_CREATE_PROJECT)}")

    def test_create_project_get(self):
        """Test create project page GET request for logged in user."""
        self.client.login(email='create@example.com', password=TEST_PASSWORD)
        response = self.client.get(reverse(URL_CREATE_PROJECT))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_CREATE_PROJECT)

    def test_create_project_post_valid(self):
        """Test creating a project with valid data."""
        self.client.login(email='create@example.com', password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_CREATE_PROJECT), {
            'name': 'New Project',
            'description': 'New Description',
            'status': TEST_PROJECT_STATUS_OPEN,
        })
        latest_project = Project.objects.latest('id')
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[latest_project.id]))
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_create_project_post_invalid(self):
        """Test creating a project with invalid data."""
        self.client.login(email='create@example.com', password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_CREATE_PROJECT), {
            'name': '',
            'description': 'Description',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_CREATE_PROJECT)


class EditProjectViewTest(TestCase):
    """Tests for the edit project view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='edit@example.com',
            name='Edit',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            name='Other',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name='Edit Project',
            description='Original Description',
            owner=self.user
        )

    def test_edit_project_get_requires_login(self):
        """Test that edit project requires login."""
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertRedirects(response, f"{reverse(URL_LOGIN)}?next={reverse(URL_EDIT_PROJECT, args=[self.project.id])}")

    def test_edit_project_owner(self):
        """Test that owner can edit project."""
        self.client.login(email='edit@example.com', password=TEST_PASSWORD)
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_project_not_owner(self):
        """Test that non-owner cannot edit project."""
        self.client.login(email='other@example.com', password=TEST_PASSWORD)
        response = self.client.get(
            reverse(URL_EDIT_PROJECT, args=[self.project.id]))
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[self.project.id]))

    def test_edit_project_post_valid(self):
        """Test editing a project with valid data."""
        self.client.login(email='edit@example.com', password=TEST_PASSWORD)
        response = self.client.post(reverse(URL_EDIT_PROJECT, args=[self.project.id]), {
            'name': 'Updated Project',
            'description': 'Updated Description',
            'status': TEST_PROJECT_STATUS_OPEN,
        })
        self.assertRedirects(response, reverse(
            URL_PROJECT_DETAILS, args=[self.project.id]))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')


class CompleteProjectViewTest(TestCase):
    """Tests for the complete project view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='complete@example.com',
            name='Complete',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.other_user = User.objects.create_user(
            email='other2@example.com',
            name='Other2',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name='Complete Project',
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
        self.client.login(email='complete@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, TEST_PROJECT_STATUS_CLOSED)

    def test_complete_project_not_owner(self):
        """Test that non-owner cannot complete project."""
        self.client.login(email='other2@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_complete_already_closed_project(self):
        """Test completing an already closed project."""
        self.project.status = TEST_PROJECT_STATUS_CLOSED
        self.project.save()
        self.client.login(email='complete@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_COMPLETE_PROJECT, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class ToggleParticipateViewTest(TestCase):
    """Tests for the toggle participate view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='participate@example.com',
            name='Participate',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.owner = User.objects.create_user(
            email='owner2@example.com',
            name='Owner',
            surname='Two',
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name='Participate Project',
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
        self.client.login(email='participate@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.user, self.project.participants.all())

    def test_toggle_participate_leave(self):
        """Test leaving a project."""
        self.project.participants.add(self.user)
        self.client.login(email='participate@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.user, self.project.participants.all())

    def test_owner_cannot_leave_project(self):
        """Test that owner cannot leave their own project."""
        self.client.login(email='owner2@example.com', password=TEST_PASSWORD)
        response = self.client.post(
            reverse(URL_TOGGLE_PARTICIPATE, args=[self.project.id]))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class FavoriteProjectsViewTest(TestCase):
    """Tests for the favorite projects view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='favorite@example.com',
            name='Favorite',
            surname=TEST_SURNAME,
            password=TEST_PASSWORD
        )
        self.owner = User.objects.create_user(
            email='owner3@example.com',
            name='Owner',
            surname='Three',
            password=TEST_PASSWORD
        )
        self.project = Project.objects.create(
            name='Favorite Project',
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
        self.client.login(email='favorite@example.com', password=TEST_PASSWORD)
        response = self.client.get(reverse(URL_FAVORITE_PROJECTS))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, TEMPLATE_FAVORITE_PROJECTS)
        self.assertIn(self.project, response.context['projects'])
