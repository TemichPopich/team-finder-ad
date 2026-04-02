from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()


class ProjectModelTest(TestCase):
    """Tests for the Project model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            name='Project',
            surname='Owner',
            password='testpass123'
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
        self.assertEqual(project.status, 'open')
    
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
        project1 = Project.objects.create(name='First', owner=self.user)
        project2 = Project.objects.create(name='Second', owner=self.user)
        
        projects = list(Project.objects.all())
        self.assertEqual(projects[0].name, 'Second')
        self.assertEqual(projects[1].name, 'First')


class ProjectListViewTest(TestCase):
    """Tests for the project list view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='list@example.com',
            name='List',
            surname='User',
            password='testpass123'
        )
        Project.objects.create(name='Open Project 1', owner=self.user, status='open')
        Project.objects.create(name='Open Project 2', owner=self.user, status='open')
        Project.objects.create(name='Closed Project', owner=self.user, status='closed')
    
    def test_project_list_get(self):
        """Test project list page GET request."""
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_list.html')
        # Only open projects should be shown
        self.assertEqual(len(response.context['projects']), 2)
    
    def test_project_list_excludes_closed(self):
        """Test that closed projects are excluded."""
        response = self.client.get(reverse('projects:project_list'))
        projects = response.context['projects']
        for project in projects:
            self.assertEqual(project.status, 'open')


class ProjectDetailsViewTest(TestCase):
    """Tests for the project details view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='details@example.com',
            name='Details',
            surname='User',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Detail Project',
            description='Project Description',
            owner=self.user
        )
    
    def test_project_details_get(self):
        """Test project details page GET request."""
        response = self.client.get(reverse('projects:project_details', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project-details.html')
        self.assertEqual(response.context['project'], self.project)
    
    def test_project_details_not_found(self):
        """Test project details with non-existent ID."""
        response = self.client.get(reverse('projects:project_details', args=[999]))
        self.assertEqual(response.status_code, 404)


class CreateProjectViewTest(TestCase):
    """Tests for the create project view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='create@example.com',
            name='Create',
            surname='User',
            password='testpass123'
        )
    
    def test_create_project_get_requires_login(self):
        """Test that create project requires login."""
        response = self.client.get(reverse('projects:create_project'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('projects:create_project')}")
    
    def test_create_project_get(self):
        """Test create project page GET request for logged in user."""
        self.client.login(email='create@example.com', password='testpass123')
        response = self.client.get(reverse('projects:create_project'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/create-project.html')
    
    def test_create_project_post_valid(self):
        """Test creating a project with valid data."""
        self.client.login(email='create@example.com', password='testpass123')
        response = self.client.post(reverse('projects:create_project'), {
            'name': 'New Project',
            'description': 'New Description',
            'status': 'open',
        })
        # Check redirect to project details (using latest project ID)
        latest_project = Project.objects.latest('id')
        self.assertRedirects(response, reverse('projects:project_details', args=[latest_project.id]))
        self.assertTrue(Project.objects.filter(name='New Project').exists())
    
    def test_create_project_post_invalid(self):
        """Test creating a project with invalid data."""
        self.client.login(email='create@example.com', password='testpass123')
        response = self.client.post(reverse('projects:create_project'), {
            'name': '',  # Name is required
            'description': 'Description',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/create-project.html')


class EditProjectViewTest(TestCase):
    """Tests for the edit project view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='edit@example.com',
            name='Edit',
            surname='User',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            name='Other',
            surname='User',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Edit Project',
            description='Original Description',
            owner=self.user
        )
    
    def test_edit_project_get_requires_login(self):
        """Test that edit project requires login."""
        response = self.client.get(reverse('projects:edit_project', args=[self.project.id]))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('projects:edit_project', args=[self.project.id])}")
    
    def test_edit_project_owner(self):
        """Test that owner can edit project."""
        self.client.login(email='edit@example.com', password='testpass123')
        response = self.client.get(reverse('projects:edit_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_project_not_owner(self):
        """Test that non-owner cannot edit project."""
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(reverse('projects:edit_project', args=[self.project.id]))
        self.assertRedirects(response, reverse('projects:project_details', args=[self.project.id]))
    
    def test_edit_project_post_valid(self):
        """Test editing a project with valid data."""
        self.client.login(email='edit@example.com', password='testpass123')
        response = self.client.post(reverse('projects:edit_project', args=[self.project.id]), {
            'name': 'Updated Project',
            'description': 'Updated Description',
            'status': 'open',
        })
        self.assertRedirects(response, reverse('projects:project_details', args=[self.project.id]))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')


class CompleteProjectViewTest(TestCase):
    """Tests for the complete project view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='complete@example.com',
            name='Complete',
            surname='User',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other2@example.com',
            name='Other2',
            surname='User',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Complete Project',
            owner=self.user,
            status='open'
        )
    
    def test_complete_project_requires_login(self):
        """Test that completing project requires login."""
        response = self.client.post(reverse('projects:complete_project', args=[self.project.id]))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('projects:complete_project', args=[self.project.id])}")
    
    def test_complete_project_owner(self):
        """Test that owner can complete project."""
        self.client.login(email='complete@example.com', password='testpass123')
        response = self.client.post(reverse('projects:complete_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'closed')
    
    def test_complete_project_not_owner(self):
        """Test that non-owner cannot complete project."""
        self.client.login(email='other2@example.com', password='testpass123')
        response = self.client.post(reverse('projects:complete_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_complete_already_closed_project(self):
        """Test completing an already closed project."""
        self.project.status = 'closed'
        self.project.save()
        self.client.login(email='complete@example.com', password='testpass123')
        response = self.client.post(reverse('projects:complete_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 400)


class ToggleParticipateViewTest(TestCase):
    """Tests for the toggle participate view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='participate@example.com',
            name='Participate',
            surname='User',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner2@example.com',
            name='Owner',
            surname='Two',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Participate Project',
            owner=self.owner,
            status='open'
        )
    
    def test_toggle_participate_requires_login(self):
        """Test that toggling participation requires login."""
        response = self.client.post(reverse('projects:toggle_participate', args=[self.project.id]))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('projects:toggle_participate', args=[self.project.id])}")
    
    def test_toggle_participate_join(self):
        """Test joining a project."""
        self.client.login(email='participate@example.com', password='testpass123')
        response = self.client.post(reverse('projects:toggle_participate', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user, self.project.participants.all())
    
    def test_toggle_participate_leave(self):
        """Test leaving a project."""
        self.project.participants.add(self.user)
        self.client.login(email='participate@example.com', password='testpass123')
        response = self.client.post(reverse('projects:toggle_participate', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.project.participants.all())
    
    def test_owner_cannot_leave_project(self):
        """Test that owner cannot leave their own project."""
        self.client.login(email='owner2@example.com', password='testpass123')
        response = self.client.post(reverse('projects:toggle_participate', args=[self.project.id]))
        self.assertEqual(response.status_code, 400)


class FavoriteProjectsViewTest(TestCase):
    """Tests for the favorite projects view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='favorite@example.com',
            name='Favorite',
            surname='User',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner3@example.com',
            name='Owner',
            surname='Three',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Favorite Project',
            owner=self.owner,
            status='open'
        )
        self.project.participants.add(self.user)
    
    def test_favorite_projects_requires_login(self):
        """Test that viewing favorites requires login."""
        response = self.client.get(reverse('projects:favorite_projects'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('projects:favorite_projects')}")
    
    def test_favorite_projects_get(self):
        """Test viewing favorite projects."""
        self.client.login(email='favorite@example.com', password='testpass123')
        response = self.client.get(reverse('projects:favorite_projects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/favorite_projects.html')
        self.assertIn(self.project, response.context['projects'])
