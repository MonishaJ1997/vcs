






from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class TrainingCourse(models.Model):
    title = models.CharField(max_length=200)
    duration_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    features = models.TextField()
    image = models.ImageField(upload_to='training/')
    brochure = models.FileField(upload_to='brochures/', blank=True, null=True)

    # FR-T-005 Webinar support
    has_webinar = models.BooleanField(default=False)

    # FR-T-004 Certificate
    has_certificate = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    def feature_list(self):
        return self.features.split(',')

    def __str__(self):
        return self.title


# FR-T-002 Enrollment + FR-T-003 Progress Tracking
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)  # 0–100%
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

   

# FR-T-004 Certificate Management
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    file = models.FileField(upload_to='certificates/')
    issued_at = models.DateTimeField(auto_now_add=True)
