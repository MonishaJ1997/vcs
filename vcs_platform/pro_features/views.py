from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import time
from datetime import datetime

@login_required
def optimize_resume(request):

    quota, created = ResumeQuota.objects.get_or_create(
        user=request.user,
        defaults={
            "total_runs": 3,
            "remaining_runs": 3,
            "month": datetime.now().month
        }
    )

    # 🔥 Monthly reset
    if quota.month != datetime.now().month:
        quota.remaining_runs = quota.total_runs
        quota.month = datetime.now().month
        quota.save()

    suggestions = None

    if quota.remaining_runs <= 0:
        messages.error(request, "Quota exhausted upgrade to Pro Plus")
        return redirect('dashboard')

    if request.method == "POST":

        resume = request.FILES.get('resume')
        jd = request.POST.get('job_description')

        time.sleep(3)

        suggestions = "Add keywords, improve format, enhance summary"

        ResumeOptimization.objects.create(
            user=request.user,
            resume=resume,
            job_description=jd,
            suggestions=suggestions
        )

        quota.remaining_runs -= 1
        quota.save()

        messages.success(request, "Resume optimized successfully")

    return render(request, 'pro_features/optimize.html', {
        "quota": quota,
        "suggestions": suggestions
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import ConsultantSession, ConsultantSessionQuota

@login_required
def schedule_session(request):
    user_type_raw = request.user.profile.user_type
    user_type = user_type_raw.lower().replace(" ", "").replace("_", "")

    perks = []
    mock_interview_info = None
    mock_interview_total = 0
    mock_interview_remaining = 0

    if user_type == "proplus":
        total_sessions = 4
        perks = [
            "4 live consultant-led mock interviews per month with detailed feedback and improvement plans",
            "4 one-to-one career mentoring sessions (30 mins each) per month; SLA of 2 business hours for escalations"
        ]
        # Fetch or create quota
        quota, _ = ConsultantSessionQuota.objects.get_or_create(
            user=request.user,
            month=datetime.now().month,
            defaults={"total_sessions": total_sessions, "remaining_sessions": total_sessions}
        )
        mock_interview_total = 4
        # Count used sessions for mock interviews
        mock_interview_used = ConsultantSession.objects.filter(
            user=request.user,
            session_date__month=datetime.now().month
        ).count()
        mock_interview_remaining = max(mock_interview_total - mock_interview_used, 0)
        mock_interview_info = {
            "total": mock_interview_total,
            "used": mock_interview_used,
            "remaining": mock_interview_remaining
        }

    elif user_type == "pro":
        total_sessions = 1
        quota, _ = ConsultantSessionQuota.objects.get_or_create(
            user=request.user,
            month=datetime.now().month,
            defaults={"total_sessions": total_sessions, "remaining_sessions": total_sessions}
        )
    elif user_type == "free":
        messages.error(request, "Free users cannot book sessions. Upgrade to Pro or Pro Plus.")
        return redirect("dashboard")
    else:
        messages.error(request, "Invalid user type.")
        return redirect("dashboard")

    # POST handling
    if request.method == "POST":
        topic = request.POST.get("topic")
        session_date_input = request.POST.get("session_date")
        if quota.remaining_sessions <= 0:
            messages.error(request, "You have used all your sessions for this month.")
            return redirect("pro_features:schedule_session")

        session_date = None
        if session_date_input and session_date_input.strip():
            if len(session_date_input) == 16:
                session_date_input += ":00"
            try:
                session_date = datetime.fromisoformat(session_date_input)
            except ValueError:
                messages.error(request, "Invalid date format. Please select a valid date and time.")
                return redirect("pro_features:schedule_session")

        session = ConsultantSession.objects.create(
            user=request.user,
            topic=topic,
            session_date=session_date,
            status="pending"
        )
        quota.remaining_sessions -= 1
        quota.save()
        messages.success(request, "Your session has been scheduled successfully!")
        return redirect("pro_features:session_success", pk=session.id)

    return render(request, "pro_features/session.html", {
        "quota": quota,
        "perks": perks,
        "mock_interview_info": mock_interview_info,
        "user_type": user_type
    })


@login_required
def session_success(request, pk):
    """
    Session success page
    """
    session = get_object_or_404(ConsultantSession, id=pk, user=request.user)
    return render(request, "pro_features/session_success.html", {"session": session})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ConsultantSession

@login_required
def my_sessions_status(request):

    sessions = ConsultantSession.objects.filter(
        user=request.user
    ).order_by('-session_date')

    return render(
        request,
        "pro_features/my_sessions_status.html",
        {"sessions": sessions}
    )
