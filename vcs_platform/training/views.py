

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TrainingCourse, Enrollment, Certificate


   # views.py
from .models import TrainingCourse, Enrollment, Certificate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import TrainingCourse, Enrollment, Certificate
from django.contrib.auth.decorators import login_required

@login_required
def training_catalog(request):
    profile = request.user.profile
    courses = TrainingCourse.objects.filter(is_active=True)
    is_pro_plus = profile.user_type == 'pro_plus'

    # Attach enrollment and certificate
    for course in courses:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        course.enrollment = enrollment
        if enrollment and enrollment.completed:
            course.user_certificate = Certificate.objects.filter(user=request.user, course=course).first()
        else:
            course.user_certificate = None

    return render(request, "training/training_catalog.html", {
        'courses': courses if is_pro_plus else [],
        'is_pro_plus': is_pro_plus
    })

from .models import TrainingCourse, Enrollment
@login_required
def enroll_course(request, course_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    profile = request.user.profile
    if profile.user_type != 'pro_plus':
        return JsonResponse({'error': 'Only Pro Plus users can enroll'}, status=403)

    # Quota enforcement: max 1 course
    existing = Enrollment.objects.filter(user=request.user).count()
    if existing >= 1:
        return JsonResponse({'error': 'Only 1 course allowed for Pro Plus'}, status=403)

    # Enroll
    course = TrainingCourse.objects.get(id=course_id, is_active=True)
    Enrollment.objects.create(user=request.user, course=course)

    return JsonResponse({'message': f"Successfully enrolled in {course.title}!"})





def user_certificates(request):
    certificates = Certificate.objects.filter(user=request.user)
    return render(request, "profile/certificates.html", {'certificates': certificates})



from .models import Certificate, Enrollment

def generate_certificate(user, course):
    # Check if already exists
    if Certificate.objects.filter(user=user, course=course).exists():
        return  # already issued

    # Generate certificate file (PDF or placeholder)
    from django.core.files.base import ContentFile
    content = ContentFile(b"Dummy certificate content for " + course.title.encode())
    cert = Certificate.objects.create(
        user=user,
        course=course,
    )
    cert.file.save(f"{course.title}_{user.username}.pdf", content)
    cert.save()


def user_certificates(request):
    certificates = Certificate.objects.filter(user=request.user)
    return render(request, "accounts/certificates.html", {'certificates': certificates})


@login_required
def complete_course(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id, user=request.user)
    enrollment.progress = 100
    enrollment.completed = True

    # Optional: create certificate
    Certificate.objects.get_or_create(user=request.user, course=enrollment.course)

    enrollment.save()
    return redirect('training-catalog')

