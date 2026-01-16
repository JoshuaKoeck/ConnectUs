from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import MEETING_TOOL_CHOICES


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with additional fields"""
    
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.'
    )
    terms = forms.BooleanField(
        required=True,
        help_text='You must agree to the terms and conditions.'
    )
    is_mentor = forms.BooleanField(
        required=True,
        label='I want to register as a mentor',
        help_text='Optional: check to sign up as a mentor.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow users to register without explicitly providing a username;
        # we'll generate one from their email if omitted.
        if 'username' in self.fields:
            self.fields['username'].required = False

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email

    def clean_username(self):
        """Check if username already exists"""
        username = self.cleaned_data.get('username')
        if not username:
            return username
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_password2(self):
        """Verify that passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        """Save the user with email"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        # If no username provided, auto-generate from email local-part
        if not user.username:
            base = user.email.split('@')[0]
            candidate = base
            i = 0
            while User.objects.filter(username=candidate).exists():
                i += 1
                candidate = f"{base}{i}"
            user.username = candidate

        if commit:
            user.save()
        return user
