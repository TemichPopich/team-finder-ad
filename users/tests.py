from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Skill

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for the custom User model."""
    
    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test',
            surname='User',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test')
        self.assertEqual(user.surname, 'User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin',
            surname='User',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_avatar_generation(self):
        """Test that avatar is generated on user creation (skipped during tests)."""
        # Avatar generation is disabled during tests to prevent file clutter
        # This test just verifies the user can be created without avatar
        user = User.objects.create_user(
            email='avatar@example.com',
            name='Avatar',
            surname='Test',
            password='testpass123'
        )
        # Avatar will be empty/None in tests (generation is skipped)
        self.assertFalse(bool(user.avatar))
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='str@example.com',
            name='John',
            surname='Doe',
            password='testpass123'
        )
        self.assertEqual(str(user), 'John Doe')


class SkillModelTest(TestCase):
    """Tests for the Skill model."""
    
    def test_create_skill(self):
        """Test creating a skill."""
        skill = Skill.objects.create(name='Python')
        self.assertEqual(skill.name, 'Python')
    
    def test_skill_str_representation(self):
        """Test skill string representation."""
        skill = Skill.objects.create(name='JavaScript')
        self.assertEqual(str(skill), 'JavaScript')
    
    def test_skill_ordering(self):
        """Test that skills are ordered by name."""
        Skill.objects.create(name='Python')
        Skill.objects.create(name='Django')
        Skill.objects.create(name='JavaScript')
        
        skills = list(Skill.objects.all())
        self.assertEqual(skills[0].name, 'Django')
        self.assertEqual(skills[1].name, 'JavaScript')
        self.assertEqual(skills[2].name, 'Python')


class UserSkillTest(TestCase):
    """Tests for user skills relationship."""
    
    def test_add_skill_to_user(self):
        """Test adding skills to a user."""
        user = User.objects.create_user(
            email='skills@example.com',
            name='Skill',
            surname='User',
            password='testpass123'
        )
        skill1 = Skill.objects.create(name='Python')
        skill2 = Skill.objects.create(name='Django')
        
        user.skills.add(skill1, skill2)
        
        self.assertIn(skill1, user.skills.all())
        self.assertIn(skill2, user.skills.all())
        self.assertEqual(user.skills.count(), 2)
    
    def test_remove_skill_from_user(self):
        """Test removing a skill from a user."""
        user = User.objects.create_user(
            email='remove@example.com',
            name='Remove',
            surname='User',
            password='testpass123'
        )
        skill = Skill.objects.create(name='Python')
        user.skills.add(skill)
        
        user.skills.remove(skill)
        
        self.assertNotIn(skill, user.skills.all())
        self.assertEqual(user.skills.count(), 0)


class RegisterViewTest(TestCase):
    """Tests for the registration view."""
    
    def test_register_get(self):
        """Test registration page GET request."""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_post_valid(self):
        """Test registration with valid data."""
        response = self.client.post(reverse('users:register'), {
            'name': 'Test',
            'surname': 'User',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertRedirects(response, reverse('projects:project_list'))
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_register_post_invalid(self):
        """Test registration with invalid data."""
        response = self.client.post(reverse('users:register'), {
            'name': 'Test',
            'surname': 'User',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Enter a valid email address')


class LoginViewTest(TestCase):
    """Tests for the login view."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='login@example.com',
            name='Login',
            surname='User',
            password='testpass123'
        )
    
    def test_login_get(self):
        """Test login page GET request."""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_post_valid(self):
        """Test login with valid credentials."""
        response = self.client.post(reverse('users:login'), {
            'username': 'login@example.com',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('projects:project_list'))
    
    def test_login_post_invalid(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('users:login'), {
            'username': 'login@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')


class ParticipantsViewTest(TestCase):
    """Tests for the participants list view."""
    
    def setUp(self):
        self.skill1 = Skill.objects.create(name='Python')
        self.skill2 = Skill.objects.create(name='JavaScript')
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            name='User',
            surname='One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            name='User',
            surname='Two',
            password='testpass123'
        )
        self.user1.skills.add(self.skill1)
        self.user2.skills.add(self.skill2)
    
    def test_participants_list(self):
        """Test participants list without filter."""
        response = self.client.get(reverse('users:participants'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/participants.html')
        self.assertEqual(len(response.context['participants']), 2)
    
    def test_participants_filter_by_skill(self):
        """Test filtering participants by skill."""
        response = self.client.get(reverse('users:participants'), {'skill': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['participants']), 1)
        # Get the first participant from the page
        participants_list = list(response.context['participants'])
        self.assertEqual(participants_list[0].email, 'user1@example.com')
