from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from accounts.models import Subscription, UserNotification
from pro_features.models import ConsultantSession, MockInterview, ConsultantSlot
from jobs.models import Job, JobApplication
from resumes.models import Resumed
from training.models import TrainingCourse, Enrollment

User = get_user_model()

def admin_dashboard(request, section=None):
    # -------- Stats --------
    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    total_resumes = Resumed.objects.count()
    total_courses = TrainingCourse.objects.count()
    total_revenue = Subscription.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_notifications = UserNotification.objects.filter(read=False).count()

    # -------- Recent Items --------
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_applications = JobApplication.objects.order_by('-applied_at')[:5]
    recent_resumes = Resumed.objects.order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.order_by('-created_at')[:5]

    # -------- Charts --------
    users_per_month = (
        User.objects.extra(select={'month': "strftime('%%m', date_joined)"})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    months = [u['month'] for u in users_per_month]
    user_counts = [u['count'] for u in users_per_month]

    revenue_per_month = (
        Subscription.objects.extra(select={'month': "strftime('%%m', created_at)"})
        .values('month')
        .annotate(total=Sum('amount_paid'))
        .order_by('month')
    )
    revenue_months = [r['month'] for r in revenue_per_month]
    revenue_values = [r['total'] or 0 for r in revenue_per_month]

    # -------- Section Data --------
    section_data = {}
    
    if section == 'users':
        section_data['items'] = User.objects.order_by('-date_joined')
    elif section == 'jobs':
        section_data['items'] = Job.objects.order_by('-created_at')
    elif section == 'applications':
        section_data['items'] = JobApplication.objects.order_by('-applied_at')
    elif section == 'resumes':
        section_data['items'] = Resumed.objects.order_by('-created_at')
    elif section == 'training':
        section_data['items'] = TrainingCourse.objects.order_by('-id')
    elif section == 'subscriptions':
        section_data['items'] = Subscription.objects.order_by('-created_at')
    elif section == 'mock_interviews':
        # Get all consultant slots
        slots = ConsultantSlot.objects.order_by('date', 'time')
        mock_interview_list = []

        for slot in slots:
            try:
                interview = MockInterview.objects.get(consultant=slot)
            except MockInterview.DoesNotExist:
                interview = None

            mock_interview_list.append({
                'slot': slot,
                'user': interview.user if interview else None,
                'interview_type': interview.interview_type if interview else None,
                'target_role': interview.target_role if interview else None,
                'scheduled_at': interview.scheduled_at if interview else None,
                'completed': interview.completed if interview else False,
                'canceled': interview.canceled if interview else False,
                'feedback_report': interview.feedback_report if interview else None,
            })
        section_data['items'] = mock_interview_list

    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_resumes': total_resumes,
        'total_courses': total_courses,
        'total_revenue': total_revenue,
        'total_notifications': total_notifications,
        'months': months,
        'user_counts': user_counts,
        'revenue_months': revenue_months,
        'revenue_values': revenue_values,
        'section': section,
        'section_data': section_data
    }

    return render(request, 'dashboard/admin_dashboard.html', context)
