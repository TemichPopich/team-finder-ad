from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Registration form with required fields."""
    
    name = forms.CharField(max_length=124, required=True)
    surname = forms.CharField(max_length=124, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['name', 'surname', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Validate phone format: 8XXXXXXXXXX or +7XXXXXXXXXX
            pattern = r'^(\+7|8)\d{10}$'
            if not re.match(pattern, phone):
                raise forms.ValidationError('Phone must be in format 8XXXXXXXXXX or +7XXXXXXXXXX')
            # Normalize to +7 format
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
        return phone


class LoginForm(AuthenticationForm):
    """Login form with email authentication."""
    
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError('This account is inactive')


class ProfileEditForm(forms.ModelForm):
    """Profile editing form."""
    
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Validate phone format: 8XXXXXXXXXX or +7XXXXXXXXXX
            pattern = r'^(\+7|8)\d{10}$'
            if not re.match(pattern, phone):
                raise forms.ValidationError('Phone must be in format 8XXXXXXXXXX or +7XXXXXXXXXX')
            # Normalize to +7 format
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            
            # Check uniqueness (exclude current user)
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Phone number already in use')
        return phone
    
    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        if github_url:
            if not github_url.startswith('https://github.com/'):
                raise forms.ValidationError('URL must be a valid GitHub profile URL')
        return github_url


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'
