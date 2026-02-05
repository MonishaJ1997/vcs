
from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'resume', 'cover_letter']

    # Custom validation for resume file
    def clean_resume_file(self):
        resume = self.cleaned_data.get('resumes/')

        if not resume:
            raise forms.ValidationError("Please upload your resume.")

        # File size limit: 5MB
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume file size cannot exceed 5MB.")

        # Only allow PDF or DOCX
        if not resume.name.endswith(('.pdf', '.docx')):
            raise forms.ValidationError("Only PDF or DOCX files are allowed.")

        return resume

    # Optional: validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@example.com'):
            # Example: restrict domain if needed
            # raise forms.ValidationError("Please use your company email.")
            pass
        return email





