from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_email_reminder(self, user_email, medication_name, medication_id, scheduled_datetime, dosage=""):
    """
    Send HTML email reminder for medication
    """
    try:
        subject = f"💊 Medication Reminder: {medication_name}"
        
        # Get current time for comparison
        current_time = timezone.now()
        
        # Parse scheduled datetime and make it timezone-aware
        if 'Z' in scheduled_datetime:
            # Handle UTC time
            scheduled_time = timezone.datetime.fromisoformat(scheduled_datetime.replace('Z', '+00:00'))
        else:
            # Handle local time - assume it's in the current timezone
            naive_scheduled = timezone.datetime.fromisoformat(scheduled_datetime)
            scheduled_time = timezone.make_aware(naive_scheduled, timezone.get_current_timezone())
        
        # Check if medication is overdue
        is_overdue = current_time > scheduled_time
        
        # Context for the email template
        context = {
            'medication_name': medication_name,
            'dosage': dosage,
            'scheduled_datetime': scheduled_time.strftime('%B %d, %Y at %I:%M %p'),
            'current_time': current_time.strftime('%B %d, %Y at %I:%M %p'),
            'is_overdue': is_overdue,
        }
        
        # Render HTML email template
        html_message = render_to_string('emails/medication_reminder.html', context)
        
        # Create plain text version
        text_message = strip_tags(html_message)
        
        # Create email with both HTML and text versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"HTML email reminder sent successfully for medication {medication_name} to {user_email}")
        return f"HTML email sent to {user_email} for {medication_name}"
        
    except Exception as e:
        logger.error(f"Failed to send email reminder: {str(e)}")
        self.retry(countdown=60, max_retries=3)  # Retry after 1 minute, max 3 times
        raise e
