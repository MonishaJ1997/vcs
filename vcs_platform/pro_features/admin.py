

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

