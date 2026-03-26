from django import forms
from .models import JobApplication
import re

class JobApplicationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',  # <-- Not example@example.com
            'class': 'form-control'
        })
    )

    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'resume', 'cover_letter']

    # Name validation
    def clean_full_name(self):
        name = self.cleaned_data.get('full_name')
        if not name:
            raise forms.ValidationError("Name is required.")
        if not re.match(r'^[A-Za-z ]+$', name):
            raise forms.ValidationError("Name should contain only letters.")
        return name

    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or email.strip() == "":
            raise forms.ValidationError("Email is required.")

        # Regex to validate email
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            raise forms.ValidationError("Enter a valid email address.")

        return email

    # Resume validation
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise forms.ValidationError("Resume is required.")
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File must be less than 5MB.")
        if not resume.name.endswith(('.pdf', '.docx')):
            raise forms.ValidationError("Only PDF or DOCX allowed.")
        return resume

    # Cover letter validation
    def clean_cover_letter(self):
        cover = self.cleaned_data.get('cover_letter')
        if not cover or cover.strip() == "":
            raise forms.ValidationError("Cover letter is required.")
        return cover