from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_catalog, name='training_catalog'),
     path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
]
