# resumes/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Resume, ResumeTemplate
from accounts.models import Subscription
 # will now always exist


@login_required
def build_resume(request):
    user = request.user
    # ✅ Safe way to get the subscription
    try:
        user_subscription = user.subscription
        user_plan = user_subscription.plan  # FREE / PRO
    except Subscription.DoesNotExist:
        # If the user has no subscription, assume FREE
        user_plan = 'FREE'

    # Fetch templates
    all_templates = ResumeTemplate.objects.all()

    if user_plan == 'FREE':
        # Only 1 template allowed for free users
        templates = all_templates[:1]
    else:
        # All templates for PRO users
        templates = all_templates

    return render(request, 'resumes/build_resume.html', {
        'templates': templates,
        'user_plan': user_plan
    })




@login_required
def create_resume(request, template_id):
    template = get_object_or_404(ResumeTemplate, id=template_id)
    user = request.user
    user_plan = user.subscription.plan

    resume_count = Resume.objects.filter(user=user).count()

    # ❌ Free user restrictions
    if user_plan == "FREE":
        if resume_count >= 1:
            return redirect("accounts:plan")  # upgrade page

        if template.is_premium:
            return redirect("accounts:plan")

    Resume.objects.create(
        user=user,
        template=template,
        title="My Resume"
    )

    return redirect("accounts:profile")



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume
from .forms import ResumeUploadForm

@login_required
def upload_resume(request):

    if request.method == "POST":

        # 🔍 check limit ONLY when submitting
        if request.user.user_type == 'free':
            resume_count = Resume.objects.filter(user=request.user).count()

            if resume_count >= 1:
                messages.error(
                    request,
                    "You already uploaded one resume. Upgrade to Pro or Pro Plus to upload multiple resumes."
                )
                return redirect('resumes:upload')

        form = ResumeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            messages.success(request, "Resume uploaded successfully.")
            return redirect('resumes:upload')

    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload.html', {'form': form})





from .utils import extract_resume_text, calculate_match
from jobs.models import Job
from .models import JobMatch
def process_resume(user, resume_instance):

    resume_text = extract_resume_text(resume_instance.file.path)

    jobs = Job.objects.all()

    for job in jobs:
        percent = calculate_match(resume_text, job.description)

        JobMatch.objects.create(
            user=user,
            job=job,
            percentage=percent
        )
    