
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from django.urls import path, include

from django.urls import path




urlpatterns = [
    # Registration
    path('register/', views.register, name='register'),

   
    # ... your other urls
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),




    path('login/', views.login_view, name='login_view'),

    # Logout (allow GET and POST for convenience)
    path(
        'logout/',
        LogoutView.as_view(next_page='dashboard', http_method_names=['get', 'post']),
        name='logout'
    ),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
   # path('accounts/', include('django.contrib.auth.urls')),
   
    path('services/', views.services, name='services'),
    

    path('free/', views.free_plan, name='free_plan'),
    path('pro/', views.pro_plan, name='pro_plan'),
    path('profile/',views.profile,name='profile'),

    #path('payment/', views.payment_page, name='payment'),
    path('payment/success/<str:plan_type>/', views.payment_success, name='payment_success'),
    path('payment/<str:plan_type>/', views.payment_page, name='payment'),

    path('invoice/download/', views.download_invoice, name='download_invoice'),


    
    path('consultant_dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('schedule-meeting/<int:application_id>/', views.schedule_meeting, name='schedule_meeting'),
    path('edit-meeting/<int:meeting_id>/', views.edit_meeting, name='edit_meeting'),
   
 



    path(
        "approve-session/<int:session_id>/",
        views.approve_session,
        name="approve_session"
    ),

    path(
        "delete-session/<int:session_id>/",
        views.delete_session,
        name="delete_session"
    ),

 
    # ...
    path('download-invoice/<int:plan_id>/', views.download_invoice, name='download_invoice'),


]





















