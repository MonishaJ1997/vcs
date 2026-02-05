# accounts/admin.py
from django.contrib import admin
from .models import User  
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

# Unregister default if needed
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass














@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'user_type', 'is_staff', 'is_superuser', 'is_active', 'date_joined'
    )
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {
            'fields': ('user_type', 'pro_subscription_active', 'whatsapp_number')
        }),
    )









from django.contrib import admin
from .models import SiteSettings

admin.site.register(SiteSettings)


from django.contrib import admin
from .models import HowItWorks

@admin.register(HowItWorks)
class HowItWorksAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order')
    list_editable = ('order',)



from django.contrib import admin
from .models import ServicePlan, ServiceFeature

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1

from django.contrib import admin
from .models import ServicePlan, ServiceFeature, Profile, Plan, Feature, Subscription

# Inline for ServiceFeature under ServicePlan
class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1  # Shows 1 empty slot by default

# Admin for ServicePlan
@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'plan_type')
    inlines = [ServiceFeatureInline]

# Admin for Plan (your second Plan model)
class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'plan_type', 'price')
    inlines = [FeatureInline]

# Admin for Subscription
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_paid', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username',)

# Admin for Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    search_fields = ('user__username',)



