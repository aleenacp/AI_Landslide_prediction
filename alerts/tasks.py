"""alerts/tasks.py — background tasks for notifications"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_alert_notifications(alert_id: int):
    """
    Background task: Send SMS + Email for an approved alert.
    Triggered from approve_alert view.
    """
    from .models import PublicAlert
    from .notifications import (send_sms, send_alert_email,
                                 get_registered_phones_for_district,
                                 get_registered_emails_for_district)

    try:
        alert = PublicAlert.objects.get(id=alert_id)
    except PublicAlert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return

    district = alert.affected_district
    message  = alert.message_english

    # SMS
    phones  = get_registered_phones_for_district(district)
    sms_ok  = sum(1 for p in phones if send_sms(p, message))
    alert.sms_sent_count = sms_ok

    # Email
    emails     = get_registered_emails_for_district(district)
    subject    = f"⚠️ Landslide {alert.severity.upper()} Alert — {district}"
    email_sent = send_alert_email(emails, subject, message)
    alert.email_sent_count = email_sent

    alert.save()
    logger.info(f"Alert {alert_id}: {sms_ok} SMS, {email_sent} emails sent")


@shared_task
def auto_run_prediction():
    """
    Scheduled task: Fetch latest satellite data and run prediction
    for high-risk zones. Run every 30 minutes via Celery Beat.
    """
    # Extend this with your ML pipeline for automated monitoring
    logger.info("Auto-prediction task triggered")