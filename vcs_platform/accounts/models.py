from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER_TYPE = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('pro_plus', 'Pro Plus'),
        ('consultant', 'Consultant'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPE,
        default='free'
    )

    pro_subscription_active = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)




from django.db import models
from django.conf import settings   # ✅ required

class Profile(models.Model):

    USER_TYPE_CHOICES = (
        ('free', 'Free User'),
        ('pro', 'Pro User'),
        ('pro_plus', 'Pro Plus User'),
        ('consultant', 'Consultant User'),
        ('admin', 'Admin User'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPE_CHOICES,
        default='free'
    )

    def __str__(self):
        return self.user.username


from django.db import models

class SiteSettings(models.Model):
    hero_background = models.ImageField(upload_to='hero/')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "VCS Site Settings"


from django.db import models

class HowItWorks(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=50,
        help_text="Bootstrap icon class (e.g. bi-person-plus)"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


from django.db import models

class ServicePlan(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('pro_plus','Pro Plus'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.plan_type})"


class ServiceFeature(models.Model):
    service_plan = models.ForeignKey(
        ServicePlan,
        related_name='features',
        on_delete=models.CASCADE
    )
    feature_text = models.CharField(max_length=255)

    def __str__(self):
        return self.feature_text


from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    PLAN_TYPE = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('pro_plus','Pro Plus'),
    )

    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.CharField(max_length=100, null=True, blank=True)  # Free = 0, Pro = 1999

    def __str__(self):
        return self.title


class Feature(models.Model):
    plan = models.ForeignKey(Plan, related_name='features', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


#class Subscription(models.Model):
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    

    #amount_paid = models.IntegerField()
    #payment_status = models.BooleanField(default=False)
    #created_at = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.conf import settings

class Subscription(models.Model):

    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription"   # ⭐ VERY IMPORTANT
    )

    

    amount_paid = models.CharField(default=0)
    payment_status = models.BooleanField(default=False)
    #is_active = models.BooleanField(default=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"




class SubscriptionNew(models.Model):   # new table
    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_new"   # new related name
    )

    plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default='FREE'
    )

    amount_paid = models.IntegerField(default=0)
    payment_status = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        # Create a default FREE subscription
        Subscription.objects.create(user=instance, plan='FREE')











from django.db import models
from django.conf import settings
from jobs.models import JobApplication

class ConsultantMeeting(models.Model):
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultant_meetings'
    )
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='meetings',
        null=True,
        blank=True
    )
    scheduled_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting: {self.consultant.username} with {self.application.user.username if self.application else 'N/A'}"



from django.db import models
from django.contrib.auth import get_user_model

user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='accounts_sessions'
)



from django.db import models
from django.contrib.auth import get_user_model

user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='accounts_sessions'
)

class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"
