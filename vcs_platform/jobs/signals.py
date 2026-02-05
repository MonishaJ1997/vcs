from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Job)
def send_job_notification(sender, instance, created, **kwargs):
    if created:  # Only send email when a new job is created
        subject = f"New Job Posted: {instance.title}"
        message = f"A new job has been posted at {instance.company} in {instance.location}.\n\nCheck it out!"
        from_email = settings.DEFAULT_FROM_EMAIL

        # Get all users (or filter Free/Pro)
        recipients = list(User.objects.values_list('email', flat=True))
        
        if recipients:
            send_mail(subject, message, from_email, recipients)
