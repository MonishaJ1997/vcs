from django.db import models

class TrainingCourse(models.Model):
    title = models.CharField(max_length=200)
    duration_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    features = models.TextField(help_text="Comma separated (Eg: 100% Job Assistance, Live Classes)")
    image = models.ImageField(upload_to='training/')
    brochure = models.FileField(upload_to='brochures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def feature_list(self):
        return self.features.split(',')

    def __str__(self):
        return self.title









from django.db import models
from django.conf import settings

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('TrainingCourse', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  # prevent duplicate enrollments

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
