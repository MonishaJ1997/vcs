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

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, create default Free subscription here
            # Subscription.objects.create(user=user, plan='FREE')
            return redirect('login')
    else:
        form = RegistrationForm()

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

    profile = request.user.profile
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





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription
from django.contrib import messages
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plan, Subscription

@login_required
def payment_page(request, plan_type):
    # Get the plan dynamically based on the type
    

    # Convert 'proplus' in URL to 'pro_plus'
    plan_type_db = plan_type.replace("proplus", "pro_plus")
    
    plan = get_object_or_404(Plan, plan_type__iexact=plan_type_db)

    if request.method == "POST":
        subscription, created = Subscription.objects.get_or_create(user=request.user)

        subscription.amount_paid = plan.price
        subscription.payment_status = True
        subscription.plan = plan.plan_type  # store string
        subscription.save()

        # Upgrade user type
        if plan.plan_type.lower() == 'pro':
            request.user.profile.user_type = "pro"
        elif plan.plan_type.lower() == 'pro_plus':
            request.user.profile.user_type = "proplus"

        request.user.profile.save()

        messages.success(request, f"✅ Payment successful! You are now a {plan.title} user.")
        return redirect('payment_success', plan_type=plan.plan_type)

    return render(request, 'accounts/payment.html', {'plan': plan})

@login_required
def payment_success(request, plan_type):
    plan = get_object_or_404(Plan, plan_type__iexact=plan_type)
    return render(request, 'accounts/success.html', {'plan': plan})

# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Plan  # or wherever your Plan model is

def download_invoice(request, plan_id):
    plan = Plan.objects.get(id=plan_id)

    template_path = 'accounts/invoice_template.html'  # create this template
    context = {'plan': plan}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{plan.title}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    
    # create pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
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
from jobs.models import JobApplication
from .models import ConsultantMeeting, UserNotification
from pro_features.models import ConsultantSession


# ✅ Consultant Role Check
def consultant_required(user):
    return (
        user.is_authenticated and
        getattr(user, "user_type", "").lower() == "consultant"
    )


# ✅ Consultant Dashboard
@login_required
@user_passes_test(consultant_required)
def consultant_dashboard(request):

    applications = JobApplication.objects.all().order_by('-applied_at')

    # 🔥 OPTION 1 — Show ONLY this consultant sessions
    sessions = ConsultantSession.objects.filter(
        consultant=request.user
    ).select_related('user').order_by('-session_date')

    # 🔥 OPTION 2 — Show ALL sessions (if needed)
    # sessions = ConsultantSession.objects.select_related(
    #     'user', 'consultant'
    # ).order_by('-session_date')

    context = {
        'applications': applications,
        'sessions': sessions
    }

    return render(request, 'accounts/consultant_dashboard.html', context)


# ✅ Approve Session
@login_required
@user_passes_test(consultant_required)
def approve_session(request, session_id):

    session = get_object_or_404(
        ConsultantSession,
        id=session_id,
        consultant=request.user
    )

    session.status = 'approved'
    session.save()

    UserNotification.objects.create(
        user=session.user,
        message=f"Your session '{session.topic}' on {session.session_date.strftime('%d %b %Y %H:%M')} has been approved."
    )

    messages.success(request, f"Session for {session.user.username} approved.")
    return redirect('consultant_dashboard')


# ✅ Cancel Session
@login_required
@user_passes_test(consultant_required)
def delete_session(request, session_id):

    session = get_object_or_404(
        ConsultantSession,
        id=session_id,
        consultant=request.user
    )

    session.status = 'cancelled'
    session.save()

    UserNotification.objects.create(
        user=session.user,
        message=f"Your session '{session.topic}' on {session.session_date.strftime('%d %b %Y %H:%M')} has been cancelled."
    )

    messages.success(request, f"Session for {session.user.username} cancelled.")
    return redirect('consultant_dashboard')







from django.contrib.auth import login, authenticate
from .forms import LoginForm

def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.user_type == "consultant":
                return redirect('consultant_dashboard')
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
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(ConsultantMeeting, id=meeting_id)

    meeting.status = 'cancelled'
    meeting.save()

    return redirect('consultant_dashboard')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_meeting(request, meeting_id):

    meeting = get_object_or_404(
        ConsultantMeeting,
        id=meeting_id,
        consultant=request.user   # security check
    )

    meeting.delete()

    return redirect('consultant_dashboard')



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



