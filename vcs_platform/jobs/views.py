from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Job, SavedJob
from django.contrib.auth.decorators import login_required

@login_required
def save_job(request):
    if request.method == "POST":
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Job, id=job_id)

        saved_job = SavedJob.objects.filter(
            user=request.user,
            job=job
        ).first()

        if saved_job:
            saved_job.delete()
            return JsonResponse({'status': 'unsaved'})
        else:
            SavedJob.objects.create(
                user=request.user,
                job=job
            )
            return JsonResponse({'status': 'saved'})

    return JsonResponse({'status': 'error'})

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Job, SavedJob
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, SavedJob

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')

    # Keyword & location filter
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(company__icontains=keyword)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)

    # Working schedule filter
    schedules_selected = request.GET.getlist('schedule')
    if schedules_selected:
        jobs = jobs.filter(working_schedule__in=schedules_selected)

    # Work type filter
    work_types_selected = request.GET.getlist('work_type')
    if work_types_selected:
        jobs = jobs.filter(work_type__in=work_types_selected)

    

    # Pagination - 6 jobs per page
    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    # Saved jobs
    saved_jobs = []
    if request.user.is_authenticated:
        saved_jobs = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)

    context = {
        'jobs': jobs,
        'saved_jobs': saved_jobs,
        'keyword': keyword,
        'location': location,
        'schedules_selected': schedules_selected,
        'work_types_selected': work_types_selected,
       
    }

    return render(request, 'jobs/job_list.html', context)



from .models import SavedJob, JobApplication

@login_required
def my_jobs(request):

    # ---------------- SAVED JOBS ----------------
    saved_jobs_qs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job')

    saved_jobs = [saved.job for saved in saved_jobs_qs]
    saved_job_ids = [job.id for job in saved_jobs]

    # ---------------- APPLIED JOBS ----------------
    applied_jobs_qs = JobApplication.objects.filter(
        user=request.user
    ).select_related('job')

    applied_jobs = [app.job for app in applied_jobs_qs]
    applied_job_ids = [job.id for job in applied_jobs]

    return render(request, 'jobs/my_jobs.html', {
        'jobs': saved_jobs,
        'saved_jobs': saved_job_ids,
        'applied_jobs': applied_jobs,
        'applied_job_ids': applied_job_ids
    })












from django.shortcuts import render, get_object_or_404
from .models import Job

def job_detail(request, pk):
    job = get_object_or_404(Job, id=pk)
    context = {'job': job}
    return render(request, 'jobs/job_detail.html', context)





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Job, JobApplication
from .forms import JobApplicationForm


# -------------------------------
# Helper Functions
# -------------------------------

def get_application_limit(user):
    user_type = user.profile.user_type.lower().strip()

    if user_type == "free":
        return 20
    elif user_type == "pro":
        return 100
    else:   # pro plus
        return None   # unlimited


def applications_this_month(user):
    start_of_month = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    return JobApplication.objects.filter(
        user=user,
        applied_at__gte=start_of_month
    ).count()


# -------------------------------
# Apply Job View
# -------------------------------

def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user = request.user

    user_type = user.profile.user_type.lower().strip()

    limit = get_application_limit(user)
    used = applications_this_month(user)

    # 🚫 Restrict before form display
    if limit is not None and used >= limit:
        if user_type == "free":
            msg = f"You've used {limit}/{limit} free applications this month. Upgrade to Pro for 100 applications/ month."
        else:
            msg = f"You've used {limit}/{limit} applications this month."

        messages.error(request, msg)
        return redirect('jobs:job_detail', pk=job.id)

    # ---------------------------
    # POST SUBMISSION
    # ---------------------------
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)

        if form.is_valid():

            # 🔥 Secure double-check
            limit = get_application_limit(user)
            used = applications_this_month(user)

            if limit is not None and used >= limit:
                return redirect('jobs:job_detail', pk=job.id)

            application = form.save(commit=False)
            application.job = job
            application.user = user
            application.save()

            used += 1

            # ℹ️ Info when limit reached after submission
            if limit is not None and used >= limit:
                if user_type == "free":
                    messages.info(
                        request,
                        f"You've used {limit}/{limit} free applications this month. Upgrade to Pro."
                    )
                else:
                    messages.info(
                        request,
                        f"You've used {limit}/{limit} applications this month."
                    )

            #messages.success(request, "Application submitted successfully!")
            return render(request, 'jobs/application_success.html', {'job': job})

    else:
        form = JobApplicationForm()

    return render(request, 'jobs/job_apply.html', {
        'job': job,
        'form': form,
        'used': used,
        'limit': limit
    })


# -------------------------------
# Upgrade View
# -------------------------------

def upgrade_to_pro(request):
    profile = request.user.profile
    profile.user_type = "Pro"
    profile.save()

    messages.success(
        request,
        "You have upgraded to Pro! Your application limit is now 100 per month."
    )

    return redirect('dashboard')





