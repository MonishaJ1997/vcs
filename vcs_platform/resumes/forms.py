from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'resume_file']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'resume_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_resume_file(self):
        resume = self.cleaned_data.get('resume_file')
        if resume:
            if resume.size > 5*1024*1024:
                raise forms.ValidationError("Resume file too large (max 5MB)")
            if not resume.name.endswith(('.pdf', '.docx')):
                raise forms.ValidationError("Resume must be PDF or DOCX")
        return resume
