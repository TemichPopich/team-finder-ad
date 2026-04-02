from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'status': forms.Select(),
        }
    
    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        if github_url:
            if not github_url.startswith('https://github.com/'):
                raise forms.ValidationError('URL must be a valid GitHub repository URL')
        return github_url
