

from django.contrib import admin
from .models import (
    ResumeQuota,
    ConsultantSessionQuota,
    ResumeOptimization,
    ConsultantSession
)

admin.site.register(ResumeQuota)
admin.site.register(ConsultantSessionQuota)
admin.site.register(ResumeOptimization)
admin.site.register(ConsultantSession)

from django.contrib import admin
from .models import UserProfile, ConsultantSlot, MockInterview


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "subscription_type", "mock_interview_quota")
    search_fields = ("user__username",)
    list_filter = ("subscription_type",)


@admin.register(ConsultantSlot)
class ConsultantSlotAdmin(admin.ModelAdmin):
    list_display = ("consultant_name", "date", "time", "is_booked")
    list_filter = ("date", "is_booked")
    search_fields = ("consultant_name",)


@admin.register(MockInterview)
class MockInterviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "consultant",
        "interview_type",
        "target_role",
        "scheduled_at",
        "completed",
        "canceled",
    )
    list_filter = ("interview_type", "completed", "canceled")
    search_fields = ("user__username", "target_role")
    autocomplete_fields = ("user", "consultant")