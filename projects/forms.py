from django import forms

from .models import Project

# Form constants
DESCRIPTION_TEXTAREA_ROWS = 6
GITHUB_URL_PREFIX = 'https://github.com/'
GITHUB_URL_ERROR_MESSAGE = 'URL must be a valid GitHub repository URL'


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': DESCRIPTION_TEXTAREA_ROWS}),
            'status': forms.Select(),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        if github_url:
            if not github_url.startswith(GITHUB_URL_PREFIX):
                raise forms.ValidationError(GITHUB_URL_ERROR_MESSAGE)
        return github_url
