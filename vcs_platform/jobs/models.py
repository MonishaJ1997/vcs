from django.db import models
from django.conf import settings

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    description = models.TextField()
    posted_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='jobs_posted'  # unique name for reverse relation
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title







class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(default='example@example.com')

    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"{self.full_name} - {self.job.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')








