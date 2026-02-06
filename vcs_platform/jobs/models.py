from django.db import models
from django.conf import settings

class Job(models.Model):
    # Basic job info
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    description = models.TextField()

    # Working schedule choices
    FULL_TIME = 'FT'
    PART_TIME = 'PT'
    INTERNSHIP = 'IN'
    WORKING_SCHEDULE_CHOICES = [
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time'),
        (INTERNSHIP, 'Internship'),
    ]
    working_schedule = models.CharField(
        max_length=2,
        choices=WORKING_SCHEDULE_CHOICES,
        default=FULL_TIME
    )

    # Work type choices
    REMOTE = 'RM'
    HYBRID = 'HY'
    ONSITE = 'ON'
    WORK_TYPE_CHOICES = [
        (REMOTE, 'Remote'),
        (HYBRID, 'Hybrid'),
        (ONSITE, 'Onsite'),
    ]
    work_type = models.CharField(
        max_length=2,
        choices=WORK_TYPE_CHOICES,
        default=ONSITE
    )

    # Salary choices
    
    salary = models.CharField(max_length=100, null=True, blank=True)

    # Posted by user
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_posted'
    )

    # Timestamps
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








