from django.contrib import admin
from .models import TrainingCourse, Enrollment, Certificate

# ---------------------------
# TrainingCourse Admin
# ---------------------------
@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_days', 'price', 'is_active', 'has_webinar', 'has_certificate')
    list_filter = ('is_active', 'has_webinar', 'has_certificate')
    search_fields = ('title',)
    readonly_fields = ('feature_list_display',)

    def feature_list_display(self, obj):
        return ", ".join(obj.feature_list())
    feature_list_display.short_description = 'Features'

# ---------------------------
# Enrollment Admin
# ---------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'progress', 'completed')
    list_filter = ('completed',)
    search_fields = ('user__username', 'course__title')

    # Add a readable "enrolled_at" column
    def enrolled_at(self, obj):
        return obj.created_at
    enrolled_at.admin_order_field = 'created_at'
    enrolled_at.short_description = 'Enrollment Date'

# ---------------------------
# Certificate Admin
# ---------------------------
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issued_at', 'file_link')
    list_filter = ('issued_at',)
    search_fields = ('user__username', 'course__title')

    def file_link(self, obj):
        if obj.file:
            return f'<a href="{obj.file.url}" target="_blank">Download</a>'
        return "-"
    file_link.allow_tags = True
    file_link.short_description = 'Certificate'
