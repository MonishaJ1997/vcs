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

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')

    keyword = request.GET.get('keyword')
    location = request.GET.get('location')

    # 🔍 Keyword search
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(company__icontains=keyword)
        )

    # 📍 Location filter
    if location:
        jobs = jobs.filter(location__icontains=location)

    # 📄 Pagination – 6 jobs per page
    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    # 🔖 Saved jobs
    saved_jobs = []
    if request.user.is_authenticated:
        saved_jobs = SavedJob.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'saved_jobs': saved_jobs,
        'keyword': keyword,
        'location': location
    })





from django.contrib.auth.decorators import login_required
from .models import SavedJob

@login_required
def my_jobs(request):
    saved_jobs_qs = SavedJob.objects.filter(user=request.user).select_related('job')

    jobs = [saved.job for saved in saved_jobs_qs]
    saved_job_ids = [job.id for job in jobs]

    return render(request, 'jobs/my_jobs.html', {
        'jobs': jobs,
        'saved_jobs': saved_job_ids
    })


from django.shortcuts import render, get_object_or_404
from .models import Job
from .forms import JobApplicationForm

def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.save()

            return render(request, 'jobs/application_success.html', {
                'job': job
            })
    else:
        form = JobApplicationForm()

    return render(request, 'jobs/job_apply.html', {
        'job': job,
        'form': form
    })





