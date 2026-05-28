"""
alerts/signals.py
Automatically creates a PublicAlert when an analysis completes
with risk_level = high or critical.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from predictions.models import LandslideAnalysis
from .models import PublicAlert


SEVERITY_MAP = {
    'high':     'warning',
    'critical': 'evacuate',
    'moderate': 'watch',
}


@receiver(post_save, sender=LandslideAnalysis)
def create_alert_on_high_risk(sender, instance, created, **kwargs):
    """Auto-generate a PublicAlert for high/critical predictions."""
    if instance.status != 'completed':
        return
    if instance.risk_level not in ('high', 'critical', 'moderate'):
        return
    # Don't create duplicate alerts
    if PublicAlert.objects.filter(analysis=instance).exists():
        return

    severity = SEVERITY_MAP.get(instance.risk_level, 'watch')
    prob_pct = round((instance.landslide_probability or 0) * 100, 1)

    msg_en = (
        f"⚠️ LANDSLIDE ALERT — {instance.location_name or 'Unknown Location'}\n"
        f"Risk Level: {instance.risk_level.upper()}\n"
        f"Probability: {prob_pct}%\n"
        f"Please follow safety instructions and move to designated shelters.\n"
        f"Emergency: 112"
    )
    msg_ml = (
        f"⚠️ ഉരുൾപൊട്ടൽ മുന്നറിയിപ്പ് — {instance.location_name or 'അജ്ഞാത സ്ഥലം'}\n"
        f"അപകട നില: {instance.risk_level.upper()}\n"
        f"ഉരുൾ സാദ്ധ്യത: {prob_pct}%\n"
        f"നിർദ്ദേശിത ആശ്രയ കേന്ദ്രങ്ങളിലേക്ക് മാറുക.\n"
        f"അടിയന്തര നമ്പർ: 112"
    )

    PublicAlert.objects.create(
        analysis=instance,
        severity=severity,
        status='pending',
        affected_district=instance.location_name or '',
        message_english=msg_en,
        message_malayalam=msg_ml,
    )