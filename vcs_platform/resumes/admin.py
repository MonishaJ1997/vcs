from django.contrib import admin
from .models import Resume


class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'resume_file', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'user__username')

admin.site.register(Resume, ResumeAdmin)
