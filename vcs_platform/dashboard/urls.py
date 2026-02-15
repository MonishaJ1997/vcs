from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('<str:section>/', views.admin_dashboard, name='admin_dashboard_section'),
]
