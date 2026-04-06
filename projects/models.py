from django.db import models
from django.conf import settings


class Project(models.Model):
    """Project model for TeamFinder platform."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.participants.filter(id=self.owner.id).exists():
            self.participants.add(self.owner)
