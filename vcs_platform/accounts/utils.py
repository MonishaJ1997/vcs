from django.core.mail import send_mail
from django.conf import settings


def send_meeting_email(user, meeting):
    subject = "Interview / Consultation Meeting Scheduled | Vetri Consultancy Services"

    message = f"""
Dear {user.username},

Greetings from Vetri Consultancy Services!

We are pleased to inform you that your consultation meeting has been successfully scheduled.
Please find the meeting details below:


 Meeting Details

Date & Time : {meeting.scheduled_at}
Notes       : {meeting.notes if meeting.notes else "N/A"}



Warm Regards,
Vetri Consultancy Services
Recruitment Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )


def send_whatsapp_message(number, message):
    print(f"WhatsApp sent to {number}: {message}")
