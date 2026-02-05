from django.contrib import admin
from .models import TrainingCourse

@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_days', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    ordering = ('price',)





from .models import  Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('course',)
