# jobs/urls.py
from django.urls import path
from . import views
app_name = 'jobs' 



urlpatterns = [
    path('job_list/', views.job_list, name='job_list'),
    path('save-job/', views.save_job, name='save_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'), 
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('<int:pk>/', views.job_detail, name='job_detail'),

]


