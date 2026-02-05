from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()  # ← this gets the actual user model class

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User  # ✅ use the model class, not string
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Create profile automatically
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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
