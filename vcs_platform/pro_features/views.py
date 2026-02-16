import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import cohere
# pro_features/views.py
from .models import ResumeQuota, ResumeOptimization, ConsultantSessionQuota, ConsultantSession

from .models import ResumeQuota, ResumeOptimization

@login_required
def optimize_resume(request):
    """
    Resume optimization using Cohere Chat API.
    Outputs structured suggestions: Keywords, Formatting, Content.
    """
    # Load Cohere API key
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    if not COHERE_API_KEY:
        messages.error(request, "Cohere API key missing. Contact admin.")
        return redirect("dashboard")

    co = cohere.Client(COHERE_API_KEY)

    # Determine user type and quota
    user_type_raw = request.user.profile.user_type
    user_type = user_type_raw.lower().replace("_", "").replace(" ", "").strip()
    total_runs = 20 if user_type == "proplus" else 3

    quota, _ = ResumeQuota.objects.get_or_create(
        user=request.user,
        defaults={"total_runs": total_runs, "remaining_runs": total_runs, "month": datetime.now().month}
    )

    # Monthly reset
    if quota.month != datetime.now().month:
        quota.remaining_runs = total_runs
        quota.month = datetime.now().month
        quota.save()

    # Upgrade reset
    if user_type == "proplus" and quota.total_runs != total_runs:
        quota.total_runs = total_runs
        quota.remaining_runs = total_runs
        quota.save()

    suggestions = None

    if quota.remaining_runs <= 0:
        messages.error(request, "Quota exhausted. Upgrade to Pro Plus.")
        return redirect("pro_features:optimize_resume")

    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description")

        if not resume_file or not job_description:
            messages.error(request, "Please upload resume and enter job description.")
            return redirect("pro_features:optimize_resume")

        # Read resume text
        resume_text = ""
        try:
            if resume_file.name.endswith(".txt"):
                resume_text = resume_file.read().decode("utf-8")
            elif resume_file.name.endswith(".pdf"):
                import PyPDF2
                reader = PyPDF2.PdfReader(resume_file)
                for page in reader.pages:
                    resume_text += page.extract_text() + "\n"
            else:
                messages.error(request, "Unsupported file format. Upload .txt or .pdf")
                return redirect("pro_features:optimize_resume")
        except Exception as e:
            messages.error(request, f"Error reading resume: {str(e)}")
            return redirect("pro_features:optimize_resume")

        # Build structured AI prompt
        prompt = f"""
You are an expert career coach and resume writer. Analyze the resume and target job description below.
Provide **structured suggestions** in three sections:

1. Keywords to Add
2. Formatting Improvements
3. Content / Summary Enhancements

Resume:
{resume_text}

Job Description:
{job_description}

Respond only in these three sections, use bullets where applicable, and make it professional.
"""

        # Call Cohere Chat API (SDK version using 'message=')
        try:
            response = co.chat(
                model="command-a-03-2025",   # latest recommended model
                message=prompt
            )
            suggestions = response.text.strip()
        except Exception as e:
            messages.error(request, f"AI error: {str(e)}")
            return redirect("pro_features:optimize_resume")

        # Save optimization record
        ResumeOptimization.objects.create(
            user=request.user,
            resume=resume_file,
            job_description=job_description,
            suggestions=suggestions
        )

        # Deduct quota
        quota.remaining_runs -= 1
        quota.save()

        messages.success(request, "Resume optimized successfully!")

    return render(request, "pro_features/optimize.html", {
        "quota": quota,
        "suggestions": suggestions
    })

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ConsultantSession, ConsultantSessionQuota


@login_required
def schedule_session(request):

    user_type = request.user.profile.user_type.lower().strip()
    user_type = request.user.profile.user_type.lower().replace("_", "").replace(" ", "").strip()

    now = datetime.now()

    # ✅ Determine plan sessions
    total_sessions = 4 if user_type == "proplus" else 1

    # ✅ Get or create quota
    quota, created = ConsultantSessionQuota.objects.get_or_create(
        user=request.user,
        month=now.month,
        defaults={
            "total_sessions": total_sessions,
            "remaining_sessions": total_sessions
        }
    )

    # ✅ Handle plan upgrade (important fix)
    if quota.total_sessions != total_sessions:

        difference = total_sessions - quota.total_sessions
        quota.total_sessions = total_sessions
        quota.remaining_sessions += difference

        # Prevent exceeding total
        if quota.remaining_sessions > total_sessions:
            quota.remaining_sessions = total_sessions

        quota.save()

    # ✅ Monthly reset
    if quota.month != now.month:
        quota.month = now.month
        quota.total_sessions = total_sessions
        quota.remaining_sessions = total_sessions
        quota.save()

    # ------------------ BOOKING ------------------
    if request.method == "POST":

        if quota.remaining_sessions <= 0:
            messages.error(request, "You have used all sessions this month.")
            return redirect("pro_features:schedule_session")

        topic = request.POST.get("topic")
        session_date_input = request.POST.get("session_date")

        session_date = None
        if session_date_input:
            try:
                if len(session_date_input) == 16:
                    session_date_input += ":00"
                session_date = datetime.fromisoformat(session_date_input)
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect("pro_features:schedule_session")

        # Create pending session
        session = ConsultantSession.objects.create(
            user=request.user,
            topic=topic,
            session_date=session_date,
            status="pending"
        )

        # ✅ Decrease quota immediately
        quota.remaining_sessions -= 1
        quota.save()

        #messages.success(request, "Session booked successfully!")
        return redirect("pro_features:session_success", pk=session.id)

    # Fetch scheduled sessions
    scheduled_sessions = ConsultantSession.objects.filter(
        user=request.user,
        session_date__month=now.month
    ).order_by("session_date")

    mock_interview_info = {
        "total": quota.total_sessions,
        "used": quota.total_sessions - quota.remaining_sessions,
        "remaining": quota.remaining_sessions
    }

    return render(request, "pro_features/session.html", {
        "quota": quota,
        "mock_interview_info": mock_interview_info,
        "scheduled_sessions": scheduled_sessions,
        "user_type": user_type
    })

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test


@login_required
@user_passes_test
def update_session_status(request, session_id):

    session = get_object_or_404(ConsultantSession, id=session_id)

    if request.method == "POST":

        new_status = request.POST.get("status")
        old_status = session.status

        now = timezone.now()
        month = session.session_date.month if session.session_date else now.month

        quota = ConsultantSessionQuota.objects.filter(
            user=session.user,
            month=month
        ).first()

        # --------------------------------------
        # ✅ RESTORE QUOTA IF CANCELLED/REJECTED
        # --------------------------------------
        if new_status in ["rejected", "cancelled"]:

            # restore only if previously counted
            if old_status == "pending" and quota:

                if quota.remaining_sessions < quota.total_sessions:
                    quota.remaining_sessions += 1
                    quota.save()

        # --------------------------------------
        # Update session status
        # --------------------------------------
        session.status = new_status
        session.save()

        messages.success(request, f"Session marked as {new_status}.")

    return redirect("consultant_dashboard")


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
    

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ConsultantSlot, MockInterview, UserProfile


@login_required
def proplus_mock_interview(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    slots = ConsultantSlot.objects.filter(is_booked=False)

    quota = {
        "remaining_sessions": profile.mock_interview_quota,
        "total_sessions": 4
    }

    perks = [
        "1:1 Expert Consultant",
        "Detailed Feedback Report",
        "Performance Analysis"
    ]

    if request.method == "POST":

        topic = request.POST.get("topic")
        target_role = request.POST.get("target_role")
        slot_id = request.POST.get("slot_id")

        # ✅ safe slot fetch
        slot = get_object_or_404(ConsultantSlot, id=slot_id)

        # ✅ create interview
        MockInterview.objects.create(
            user=request.user,
            consultant=slot,
            interview_type=topic,
            target_role=target_role
        )

        # ✅ mark slot booked
        slot.is_booked = True
        slot.save()

        # ✅ reduce quota
        profile.mock_interview_quota -= 1
        profile.save()
        if request.user.email:

            subject = "🎯 Mock Interview Scheduled Successfully"

            message = f"""
Hello {request.user.username},

Your Mock Interview has been successfully scheduled.

📌 Interview Type: {topic}
🎯 Target Role: {target_role}
📅 Date & Time: {slot.date} {slot.time}

You will receive further updates from your consultant soon.

Best Regards,
Vetri Consultancy Services
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        # ✅ SUCCESS MESSAGE
        messages.success(request, "Mock Interview Scheduled Successfully ✅")

        #return redirect("proplus_mock_interview")

    context = {
        "slots": slots,
        "quota": quota,
        "perks": perks
    }

    return render(request, "pro_features/proplus_booking.html", context)


@login_required
def consultant_booking(request):

    booked_types = MockInterview.objects.filter(
        user=request.user,
        canceled=False
    ).values_list("interview_type", flat=True)

    context = {
        "booked_types": list(booked_types)
    }

    return render(request, "pro_features/consultant_booking.html", context)