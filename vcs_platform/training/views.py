from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TrainingCourse

#@login_required
#def training_catalog(request):
    #courses = TrainingCourse.objects.filter(is_active=True)
    #return render(request, 'training/training_catalog.html', {
        #'courses': courses
    #})




from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TrainingCourse, Enrollment

@login_required
def training_catalog(request):
    courses = TrainingCourse.objects.filter(is_active=True)
    
    is_pro = False
    if hasattr(request.user, 'profile') and getattr(request.user.profile, 'user_type', 'free') == 'pro':
        is_pro = True

    return render(request, 'training/training_catalog.html', {
        'courses': courses,
        'is_pro': is_pro
    })



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import TrainingCourse
from accounts.models import Profile

@login_required
def enroll_course(request, course_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # Get course
    course = get_object_or_404(TrainingCourse, id=course_id, is_active=True)

    # Check user type
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)

    if profile.user_type != 'pro':
        return JsonResponse({'error': 'Only Pro users can enroll', 'user_type': 'Free'}, status=403)

    # Here, create enrollment logic (e.g., save Enrollment model)
    # For simplicity, we just return success message
    return JsonResponse({
        'message': f"You have successfully enrolled in {course.title}!",
        'user_type': 'Pro'
    })
