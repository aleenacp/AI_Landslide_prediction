"""alerts/notifications.py — SMS, Email, Push notification senders"""
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


def send_sms(to_number: str, message: str) -> bool:
    """Send SMS via Twilio. Returns True on success."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number,
        )
        return True
    except Exception as e:
        logger.error(f"SMS failed to {to_number}: {e}")
        return False


def send_alert_email(to_emails: list, subject: str, message: str) -> int:
    """Send email alert. Returns number sent."""
    sent = 0
    for email in to_emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            sent += 1
        except Exception as e:
            logger.error(f"Email failed to {email}: {e}")
    return sent


def get_registered_phones_for_district(district: str) -> list:
    """
    Return list of phone numbers registered for a district.
    In production: query a UserProfile model with district + phone fields.
    For now: returns test numbers from settings (ALERT_TEST_PHONES).
    """
    return getattr(settings, 'ALERT_TEST_PHONES', [])


def get_registered_emails_for_district(district: str) -> list:
    """Return emails for district. Extend with a UserProfile query."""
    from django.contrib.auth.models import User
    # Return emails of all staff (govt officers) + registered civilians
    return list(
        User.objects.filter(is_staff=True, email__isnull=False)
                    .values_list('email', flat=True)
    )