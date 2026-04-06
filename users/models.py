import random
import hashlib
import sys
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io


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
    name = models.CharField(max_length=124, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as the primary identifier."""
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    about = models.TextField(max_length=256, blank=True, default='')
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
            self.generate_avatar()
        super().save(*args, **kwargs)
    
    def generate_avatar(self):
        """Generate avatar with first letter of name on colored background."""
        size = (200, 200)
        background_color = self._get_random_color()
        text_color = (255, 255, 255)
        
        img = Image.new('RGB', size, color=background_color)
        draw = ImageDraw.Draw(img)        

        initial = self.name[0].upper() if self.name else '?'
        
        
        font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), initial, fill=text_color, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"avatar_{hashlib.md5(self.email.encode()).hexdigest()}.png"
        self.avatar.save(filename, ContentFile(buffer.read()), save=False)
    
    def _get_random_color(self):
        """Get a random pleasant background color."""
        colors = [
            (65, 105, 225),   
            (34, 139, 34),    
            (220, 20, 60),
            (255, 140, 0),   
            (148, 0, 211),    
            (0, 139, 139),    
            (218, 112, 214),  
            (70, 130, 180),   
            (50, 205, 50),    
            (255, 99, 71),    
        ]

        hash_val = int(hashlib.md5(self.email.encode()).hexdigest(), 16)
        return colors[hash_val % len(colors)]
