from django.urls import path
from . import views

app_name = "resumes"

urlpatterns = [
    path("build/", views.build_resume, name="build_resume"),
]


# resumes/urls.py
from django.urls import path
from . import views

app_name = "resumes"

urlpatterns = [
    #path("build/", views.build_resume, name="build_resume"),
    #path("create/<int:template_id>/", views.create_resume, name="create_resume"),
    path("upload/",views.upload_resume, name="upload"),
]


    
