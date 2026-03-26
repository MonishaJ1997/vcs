from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.models import HowItWorks
from accounts.models import ServicePlan
# accounts/views.py
from pro_features.models import ConsultantSession  # Use the session from pro_features



User = get_user_model()

# accounts/views.py

from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib import messages

def register(request):
    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Successful!")
            return redirect('login')  # reload page

    return render(request, 'accounts/register.html', {'form': form})

# accounts/views.py
from django.shortcuts import render
from chatbot.models import ChatMessage  # if needed
from .models import User  # your custom user
from accounts.models import SiteSettings  # <-- IMPORT YOUR MODEL HERE
from django.contrib.auth.decorators import login_required




@login_required
def dashboard(request):

    settings = SiteSettings.objects.last()
    steps = HowItWorks.objects.all()
    plans = Plan.objects.all()
    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )
    #profile = request.user.profile
    user_type = profile.user_type

    return render(request, 'accounts/dashboard.html', {
        'settings': settings,
        'steps': steps,
        'plans': plans,
        'user_type': user_type
    })



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Plan
from django.contrib import messages

def services(request):
    plans = Plan.objects.all()
    return render(request, 'accounts/services.html', {'plans': plans})

def free_plan(request):
    plan = Plan.objects.filter(plan_type='free').first()
    if not plan:
        messages.error(request, "Free Plan is not available.")
        return redirect('services')
    features = plan.features.all()
    return render(request, 'accounts/free.html', {'plan': plan, 'features': features})

@login_required
def pro_plan(request):
    plan = Plan.objects.filter(plan_type='pro').first()
    if not plan:
        messages.error(request, "Pro Plan is not available.")
        return redirect('services')
    features = plan.features.all()
    return render(request, 'accounts/pro.html', {'plan': plan, 'features': features})

import stripe
import json

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from .models import Plan, Subscription, Profile

if not settings.STRIPE_SECRET_KEY:
    raise Exception("⚠️ STRIPE_SECRET_KEY is missing! Set it in .env or Render dashboard.")

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_page(request, plan_type):

    plan_type_db = plan_type.replace("proplus", "pro_plus")

    plan = get_object_or_404(
        Plan,
        plan_type__iexact=plan_type_db
    )

    # ---------------------------
    # AJAX POST AFTER STRIPE
    # ---------------------------
    if request.method == "POST":

        print("🔥 POST HIT")

        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"status": "bad_json"})

        payment_intent_id = data.get("payment_intent_id")
        print("🔥 Payment Intent:", payment_intent_id)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception as e:
            print("❌ Stripe Error:", e)
            return JsonResponse({"status": "failed"})

        print("🔥 Stripe Status:", intent.status)

        if intent.status == "succeeded":

            # ------------------
            # SAVE SUBSCRIPTION
            # ------------------
            subscription, created = Subscription.objects.get_or_create(
                user=request.user
            )

            subscription.plan = plan.plan_type
            subscription.amount_paid = plan.price
            subscription.payment_status = True
            subscription.save()

            # ------------------
            # 🔥 PROFILE SAFE UPDATE
            # ------------------
            profile, created = Profile.objects.get_or_create(
                user=request.user
            )

            print("🔥 BEFORE:", profile.user_type)

            if plan.plan_type.lower() == "pro":
                profile.user_type = "pro"

            elif plan.plan_type.lower() == "pro_plus":
                profile.user_type = "pro_plus"

            profile.save()

            print("🔥 AFTER:", profile.user_type)

            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "failed"})

    # ---------------------------
    # CREATE PAYMENT INTENT
    # ---------------------------
    intent = stripe.PaymentIntent.create(
        amount=int(float(plan.price) * 100),
        currency="inr",
        payment_method_types=["card"],
        metadata={
            "user_id": request.user.id,
            "plan": plan.plan_type
        }
    )

    return render(
        request,
        "accounts/payment.html",
        {
            "plan": plan,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "client_secret": intent.client_secret
        }
    )


@login_required
def payment_success(request, plan_type):

    plan = get_object_or_404(
        Plan,
        plan_type__iexact=plan_type
    )

    messages.success(
        request,
        f" Payment successful! You are now a {plan.title} user."
    )

    return render(
        request,
        "accounts/success.html",
        {"plan": plan}
    )









from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Plan

@login_required
def download_invoice(request, plan_id):
    """
    Generates a professional PDF invoice with safe date handling.
    """
    plan = get_object_or_404(Plan, id=plan_id)

    # Use plan.created_at if it exists; fallback to current date
    invoice_date = getattr(plan, 'created_at', timezone.now())

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()
    styleH = styles['Heading1']
    styleN = styles['Normal']

    # HEADER
    elements.append(Paragraph("Invoice", styleH))
    elements.append(Paragraph("Subscription Payment Confirmation", styleN))
    elements.append(Spacer(1, 12))

    # USER & PLAN DETAILS
    elements.append(Paragraph(f"<b>Customer:</b> {request.user.get_full_name()}", styleN))
    elements.append(Paragraph(f"<b>Email:</b> {request.user.email}", styleN))
    elements.append(Paragraph(f"<b>Plan:</b> {plan.title}", styleN))
    elements.append(Paragraph(f"<b>Amount Paid:</b> ₹ {plan.price}", styleN))
    elements.append(Paragraph(f"<b>Status:</b> Active", styleN))
    elements.append(Paragraph(f"<b>Date:</b> {invoice_date.strftime('%d %b %Y')}", styleN))
    elements.append(Spacer(1, 12))

    # TABLE FOR LINE ITEMS
    data = [
        ['Description', 'Amount (₹)'],
        [f'{plan.title} Subscription', f'{plan.price}']
    ]
    table = Table(data, colWidths=[350, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f8a70')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#ddd')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # FOOTER
    elements.append(Paragraph("Generated by Vetri Consultancy Services", styleN))
    elements.append(Paragraph("Contact: info@vetriconsultancy.com | +91 9876543210", styleN))

    # BUILD PDF
    doc.build(elements)

    # RETURN RESPONSE
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{plan.title}.pdf"'
    return response
  # ✅ CORRECT

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from resumes.models import Resume





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from resumes.models import Resume

from accounts.models import Profile

@login_required
def profile(request):
    resume = Resume.objects.filter(user=request.user).first()
    
   
    skills = []

    # Safe skill parsing
    if resume and getattr(resume, 'skills', None):
        skills = [s.strip().lower() for s in resume.skills.split(',') if s.strip()]
        if skills:
            query = Q()
            for skill in skills:
                query |= Q(description__icontains=skill)
            
    # Ensure UserProfile exists
    profile, _ = Profile.objects.get_or_create(user=request.user)

    return render(request, 'accounts/profile.html', {
        'resume': resume,
        
        
        'profile': profile
    })

@login_required
def upload_resume(request):
    if request.method == 'POST':
        Resume.objects.update_or_create(
            user=request.user,
            defaults={
                'file': request.FILES['resume'],
                'skills': request.POST['skills']
            }
        )
        return redirect('profile')

    return render(request, 'accounts/upload_resume.html')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        })
    





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from jobs.models import JobApplication
from .models import ConsultantMeeting, UserNotification
from pro_features.models import ConsultantSession
from .forms import ConsultantMeetingForm

# ✅ Consultant Role Check
def consultant_required(user):
    return user.is_authenticated and getattr(user, "user_type", "").lower() == "consultant"


# ✅ Consultant Dashboard
@login_required
@user_passes_test(consultant_required)
def consultant_dashboard(request):
    applications = JobApplication.objects.all().order_by('-applied_at')

    # Show all sessions (can filter to this consultant if needed)
    sessions = ConsultantSession.objects.select_related('user', 'consultant').order_by('-session_date')

    context = {
        'applications': applications,
        'sessions': sessions
    }
    return render(request, 'accounts/consultant_dashboard.html', context)

@login_required
@user_passes_test(consultant_required)
def approve_session(request, session_id):
    try:
        session = ConsultantSession.objects.get(id=session_id)
    except ConsultantSession.DoesNotExist:
        messages.error(request, "No session found.")
        return redirect("consultant_dashboard")

    if session.status != "approved":

        session.status = "approved"
        session.save()

        UserNotification.objects.create(
            user=session.user,
            message=f"Your session '{session.topic}' on "
                    f"{session.session_date.strftime('%d %b %Y %H:%M')} has been approved."
        )

        if session.user.email:
            send_mail(
                subject="✅ Your Consultant Session is Approved",
                message=f"Hello {session.user.username},\n\n"
                        f"Your session '{session.topic}' scheduled for "
                        f"{session.session_date.strftime('%d %b %Y %H:%M')} "
                        f"has been APPROVED.\n\n"
                        "Thank you,\nVetri Consultancy Services",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.user.email],
                fail_silently=False
            )

    else:
        messages.info(request, "This session is already approved.")

    return redirect("consultant_dashboard")




@login_required
@user_passes_test(consultant_required)
def delete_session(request, session_id):
    try:
        session = ConsultantSession.objects.get(id=session_id)
    except ConsultantSession.DoesNotExist:
        messages.error(request, "No session found.")
        return redirect("consultant_dashboard")

    if session.status != "cancelled":

        # 🔥 ADD BACK QUOTA ONLY IF NOT ALREADY CANCELLED
        from pro_features.models import ConsultantSessionQuota

        try:
            quota = ConsultantSessionQuota.objects.get(
                user=session.user,
                month=session.session_date.month
            )

            # Prevent exceeding total_sessions
            if quota.remaining_sessions < quota.total_sessions:
                quota.remaining_sessions += 1
                quota.save()

        except ConsultantSessionQuota.DoesNotExist:
            pass  # safety fallback

        session.status = "cancelled"
        session.save()

        UserNotification.objects.create(
            user=session.user,
            message=f"Your session '{session.topic}' on "
                    f"{session.session_date.strftime('%d %b %Y %H:%M')} has been cancelled."
        )

        if session.user.email:
            send_mail(
                subject="❌ Your Consultant Session is Cancelled",
                message=f"Hello {session.user.username},\n\n"
                        f"Your session '{session.topic}' scheduled for "
                        f"{session.session_date.strftime('%d %b %Y %H:%M')} "
                        f"has been CANCELLED by {request.user.username}.\n\n"
                        "Please contact support or reschedule if needed.\n"
                        "Thank you,\nVetri Consultancy Services",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.user.email],
                fail_silently=False
            )

    else:
        messages.info(request, "This session is already cancelled.")

    return redirect("consultant_dashboard")




from pro_features.models import ConsultantSessionQuota
@login_required
@user_passes_test(consultant_required)
def update_session_status(request, session_id):

    session = get_object_or_404(ConsultantSession, id=session_id)

    new_status = request.POST.get("status")  # approved / rejected / cancelled
    old_status = session.status

    # Get correct month safely
    month = session.session_date.month if session.session_date else datetime.now().month

    try:
        quota = ConsultantSessionQuota.objects.get(
            user=session.user,
            month=month
        )
    except ConsultantSessionQuota.DoesNotExist:
        quota = None

    # 🔥 If rejected or cancelled → Add quota back
    if new_status in ["rejected", "cancelled"]:

        if old_status not in ["rejected", "cancelled"] and quota:

            if quota.remaining_sessions < quota.total_sessions:
                quota.remaining_sessions += 1
                quota.save()

    # Approve → No change
    session.status = new_status
    session.save()

    messages.success(request, f"Session marked as {new_status}.")
    return redirect("consultant_dashboard")


from django.contrib.auth import login, authenticate
from .forms import LoginForm

def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            if user.user_type == "trainee":
                messages.error(request, "Trainees must login from the trainee login page.")
                return redirect('login')
            login(request, user)

            if user.user_type == "consultant":
                return redirect('consultant_dashboard')
            elif user.user_type == "admin":
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})


from .utils import send_meeting_email, send_whatsapp_message

@login_required
@user_passes_test(consultant_required)
def schedule_meeting(request, application_id=None):

    application = get_object_or_404(JobApplication, id=application_id)

    if request.method == 'POST':
        form = ConsultantMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.consultant = request.user
            meeting.application = application
            meeting.save()

            user = application.user

            # EMAIL FOR ALL USERS
            send_meeting_email(user, meeting)

            # WHATSAPP ONLY FOR PRO USERS
            if user.user_type == 'pro':
                send_whatsapp_message(
                    user.whatsapp_number,
                    f"Meeting scheduled at {meeting.scheduled_at}"
                )

            return redirect('consultant_dashboard')

    else:
        form = ConsultantMeetingForm()

    return render(request,'accounts/schedule_meeting.html',{
        'form':form,
        'application':application
    })


@login_required
@user_passes_test(consultant_required)
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(ConsultantMeeting, id=meeting_id)

    if request.method == "POST":
        form = ConsultantMeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('consultant_dashboard')
    else:
        form = ConsultantMeetingForm(instance=meeting)

    return render(request,'accounts/schedule_meeting.html',{'form':form})





























import re
from django.contrib import messages
from django.shortcuts import redirect

def payment_view(request):

    if request.method == "POST":
        card_name = request.POST.get("card_name")
        card_number = request.POST.get("card_number").replace(" ","")
        expiry = request.POST.get("expiry")
        cvv = request.POST.get("cvv")

        if len(card_number) != 16 or not card_number.isdigit():
            messages.error(request,"Invalid card number")
            return redirect("payment")

        if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', expiry):
            messages.error(request,"Invalid expiry format")
            return redirect("payment")

        if len(cvv) != 3 or not cvv.isdigit():
            messages.error(request,"Invalid CVV")
            return redirect("payment")

        # SUCCESS
        messages.success(request,"Payment successful")
        return redirect("dashboard")

    return render(request,"payment.html")

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def trainee_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.user_type == "trainee":

                # 🔥 Automatically upgrade to pro_plus
                user.profile.user_type = "pro_plus"
                user.profile.save()

                login(request, user)
                return redirect("dashboard")   # or wherever you want

            else:
                messages.error(request, "Only trainees can login here.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/trainee_login.html")



def support(request):
    return render(request, 'accounts/support.html')

def delivery(request):
    return render(request, 'accounts/delivery.html')

def terms(request):
    return render(request, 'accounts/terms.html')

def privacy(request):
    return render(request, 'accounts/privacy.html')




from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

@login_required
def update_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user

            username = data.get("username", "").strip()
            email = data.get("email", "").strip()
            whatsapp = data.get("whatsapp", "").strip()

            if not username or not email:
                return JsonResponse({"success": False, "error": "Username and email are required."})

            # Update user fields
            user.username = username
            user.email = email
            user.save()

            # Update profile fields
            profile = getattr(user, "profile", None)
            if profile:
                profile.whatsapp_number = whatsapp
                profile.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})