from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ResumeQuota(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    total_runs = models.IntegerField(default=3)
    remaining_runs = models.IntegerField(default=3)
    month = models.IntegerField()

    def __str__(self):
        return f"{self.user} Resume Quota"


class ConsultantSessionQuota(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    total_sessions = models.IntegerField(default=1)
    remaining_sessions = models.IntegerField(default=1)
    month = models.IntegerField()

    def __str__(self):
        return f"{self.user} Session Quota"


class ResumeOptimization(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    job_description = models.TextField()
    suggestions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



from django.conf import settings
from django.db import models
from datetime import datetime

class ConsultantSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultant_sessions'
    )
    topic = models.CharField(max_length=255)
    session_date = models.DateTimeField(null=True, blank=True)  # allow nulls safely
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def save(self, *args, **kwargs):
    if isinstance(self.session_date, str) and self.session_date.strip() != "":
        try:
            self.session_date = datetime.fromisoformat(self.session_date)
        except ValueError:
            self.session_date = None  # fallback instead of crashing
    super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.topic}"
