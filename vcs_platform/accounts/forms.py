from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
import re

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    # ✅ Name validation
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[A-Za-z ]+$', username):
            raise forms.ValidationError("Name should contain only letters")
        return username

    # ✅ Email validation
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    # ✅ PASSWORD VALIDATION (FIXED INSIDE CLASS)
    def clean_password(self):
        password = self.cleaned_data.get('password')

        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{7,}$'

        if not re.match(password_regex, password):
            raise forms.ValidationError(
                "Password must be at least 7 characters and include a letter, number, and special character"
            )

        return password

    # ✅ SAVE METHOD (FIXED INDENTATION)
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user


from django import forms
from .models import ConsultantMeeting

class ConsultantMeetingForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Meeting Date & Time"
    )

    class Meta:
        model = ConsultantMeeting
        fields = ['application', 'scheduled_at', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }










from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Name',
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'
        })
    )