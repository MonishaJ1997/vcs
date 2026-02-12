from django.urls import path
from .views import *
from . import views

app_name = "pro_features"   # ⭐ VERY IMPORTANT

urlpatterns = [
    path('optimize/', views.optimize_resume, name='optimize_resume'),
    path('session/', views.schedule_session, name='schedule_session'),
    path("session-success/<int:pk>/", views.session_success, name="session_success"),


    path(
        "my-sessions/",
        views.my_sessions_status,
        name="my_sessions_status"
    ),




    path('mock-interview/', views.proplus_mock_interview, name='proplus_mock_interview'),
    
]




