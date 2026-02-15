# chatbot/urls.py
from django.urls import path
from .views import ChatbotAskView
from django.views.generic import TemplateView
from .views import ChatbotAskView, ChatbotUploadResumeView

urlpatterns = [
    path('', TemplateView.as_view(template_name='chatbot/chatbot.html'), name='chatbot-home'),
    path('ask/', ChatbotAskView.as_view(), name='chatbot-ask'),
    path('upload-resume/', ChatbotUploadResumeView.as_view(), name='chatbot-upload-resume'),
]