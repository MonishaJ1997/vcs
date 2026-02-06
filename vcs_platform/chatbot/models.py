# chatbot/models.py
from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField(blank=True)
    escalated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"



class CompanyInterviewQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('coding', 'Coding'),
        ('behavioral', 'Behavioral'),
        ('hr', 'HR'),
    ]

    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField()
    difficulty = models.CharField(max_length=20, blank=True, null=True)



class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
