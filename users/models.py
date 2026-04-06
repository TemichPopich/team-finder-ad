import sys

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Model constants
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 20
ABOUT_MAX_LENGTH = 256


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class Skill(models.Model):
    """Skill model for user skills (Variant 2)."""
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as the primary identifier."""

    email = models.EmailField(unique=True, max_length=EMAIL_MAX_LENGTH)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    skills = models.ManyToManyField(Skill, related_name='users', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        is_test = 'test' in sys.argv or 'pytest' in sys.modules
        is_new = self.pk is None
        if is_new and not self.avatar and not is_test:
            from .utils import generate_avatar
            generate_avatar(self)
        super().save(*args, **kwargs)
