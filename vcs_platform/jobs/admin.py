from django.contrib import admin
from .models import Job, SavedJob

# -------------------------------
# Job Admin
# -------------------------------
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'experience', 'created_at')
    search_fields = ('title', 'company', 'location', 'experience')
    list_filter = ('location', 'experience', 'created_at')
    ordering = ('-created_at',)

# -------------------------------
# SavedJob Admin
# -------------------------------
@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    search_fields = ('user__username', 'job__title', 'job__company')
    list_filter = ('saved_at',)
    ordering = ('-saved_at',)
