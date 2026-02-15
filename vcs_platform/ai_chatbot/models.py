from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()
    reply = models.TextField()
    cost = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_count = models.IntegerField(default=0)
    last_reset = models.DateField(auto_now_add=True)



class ChatEscalation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    priority = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
