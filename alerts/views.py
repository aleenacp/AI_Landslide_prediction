"""alerts/views.py"""
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (PublicAlert, GovernmentApproval, SafetyInstruction,
                     EmergencyContact, Shelter)
from .tasks import send_alert_notifications  # we create this in Step 13


def is_officer(user):
    """Allow staff/superuser access to govt dashboard."""
    return user.is_staff or user.is_superuser


# ── PUBLIC ALERT LIST (API) ──────────────────────────────────────────────────
class PublicAlertListAPI(APIView):
    """GET /api/alerts/ — list approved alerts for public display."""

    def get(self, request):
        alerts = PublicAlert.objects.filter(status='approved').order_by('-created_at')[:20]
        data = []
        for a in alerts:
            data.append({
                'id':               a.id,
                'severity':         a.severity,
                'affected_district':a.affected_district,
                'affected_ward':    a.affected_ward,
                'message_english':  a.message_english,
                'message_malayalam':a.message_malayalam,
                'sent_at':          a.sent_at.isoformat() if a.sent_at else None,
                'probability':      a.analysis.landslide_probability,
                'risk_level':       a.analysis.risk_level,
                'latitude':         a.analysis.latitude,
                'longitude':        a.analysis.longitude,
            })
        return Response(data)


# ── SAFETY INSTRUCTIONS (API) ───────────────────────────────────────────────
class SafetyInstructionsAPI(APIView):
    """GET /api/safety-instructions/?severity=high"""

    def get(self, request):
        severity = request.query_params.get('severity', 'all')
        severity_order = ['all', 'moderate', 'high', 'critical']
        # Return instructions for this level and below
        if severity in severity_order:
            idx = severity_order.index(severity)
            relevant = severity_order[:idx + 1]
        else:
            relevant = severity_order

        qs = SafetyInstruction.objects.filter(
            is_active=True, severity__in=relevant
        )
        data = [{
            'id':        i.id,
            'icon':      i.icon,
            'category':  i.category,
            'title_en':  i.title_en,
            'title_ml':  i.title_ml,
            'body_en':   i.body_en,
            'body_ml':   i.body_ml,
        } for i in qs]
        return Response(data)


# ── EMERGENCY CONTACTS (API) ─────────────────────────────────────────────────
class EmergencyContactsAPI(APIView):
    """GET /api/emergency-contacts/?district=Wayanad"""

    def get(self, request):
        district = request.query_params.get('district', '')
        qs = EmergencyContact.objects.filter(is_active=True)
        if district:
            qs = qs.filter(district__icontains=district) | \
                 EmergencyContact.objects.filter(is_active=True, district='')
        data = [{
            'id':       c.id,
            'name':     c.name,
            'category': c.category,
            'phone':    c.phone,
            'alt_phone':c.alt_phone,
            'email':    c.email,
            'district': c.district,
        } for c in qs.distinct()]
        return Response(data)


# ── SHELTERS (API) ───────────────────────────────────────────────────────────
class ShelterListAPI(APIView):
    """GET /api/shelters/?lat=10.5&lon=76.1&radius=50"""

    def get(self, request):
        qs = Shelter.objects.filter(is_open=True)
        data = [{
            'id':              s.id,
            'name':            s.name,
            'address':         s.address,
            'district':        s.district,
            'latitude':        s.latitude,
            'longitude':       s.longitude,
            'capacity':        s.capacity,
            'current_occupancy':s.current_occupancy,
            'available_capacity':s.available_capacity,
            'occupancy_percent': s.occupancy_percent,
            'has_food':        s.has_food,
            'has_medical':     s.has_medical,
            'contact_name':    s.contact_name,
            'contact_phone':   s.contact_phone,
        } for s in qs]
        return Response(data)


class ShelterUpdateAPI(APIView):
    """POST /api/shelters/<id>/update/ — update occupancy"""

    def post(self, request, pk):
        shelter = get_object_or_404(Shelter, pk=pk)
        occupancy = request.data.get('current_occupancy')
        is_open   = request.data.get('is_open')
        if occupancy is not None:
            shelter.current_occupancy = int(occupancy)
        if is_open is not None:
            shelter.is_open = bool(is_open)
        shelter.save()
        return Response({'status': 'updated', 'id': shelter.id})


# ── GOVERNMENT DASHBOARD (HTML view) ────────────────────────────────────────
@login_required
@user_passes_test(is_officer)
def government_dashboard(request):
    pending_alerts   = PublicAlert.objects.filter(status='pending').order_by('-created_at')
    approved_alerts  = PublicAlert.objects.filter(status='approved').order_by('-created_at')[:10]
    rejected_alerts  = PublicAlert.objects.filter(status='rejected').order_by('-created_at')[:5]
    total_shelters   = Shelter.objects.count()
    open_shelters    = Shelter.objects.filter(is_open=True).count()

    return render(request, 'alerts/govt_dashboard.html', {
        'pending_alerts':  pending_alerts,
        'approved_alerts': approved_alerts,
        'rejected_alerts': rejected_alerts,
        'total_shelters':  total_shelters,
        'open_shelters':   open_shelters,
    })


@login_required
@user_passes_test(is_officer)
@require_POST
def approve_alert(request, pk):
    """Approve alert → trigger notification pipeline."""
    alert = get_object_or_404(PublicAlert, pk=pk)
    notes = request.POST.get('notes', '')

    GovernmentApproval.objects.create(
        alert=alert,
        officer=request.user,
        action='approved',
        notes=notes,
    )
    alert.status  = 'approved'
    alert.sent_at = timezone.now()
    alert.save()

    # Trigger async notification task (Celery)
    send_alert_notifications.delay(alert.id)

    return redirect('govt-dashboard')


@login_required
@user_passes_test(is_officer)
@require_POST
def reject_alert(request, pk):
    alert = get_object_or_404(PublicAlert, pk=pk)
    notes = request.POST.get('notes', '')

    GovernmentApproval.objects.create(
        alert=alert,
        officer=request.user,
        action='rejected',
        notes=notes,
    )
    alert.status = 'rejected'
    alert.save()
    return redirect('govt-dashboard')


# ── AREA WARNING MAP DATA (API) ──────────────────────────────────────────────
class AreaWarningMapAPI(APIView):
    """GET /api/area-warnings/ — GeoJSON-style data for Leaflet map"""

    def get(self, request):
        from predictions.models import LandslideAnalysis
        analyses = LandslideAnalysis.objects.filter(
            status='completed',
            latitude__isnull=False,
            longitude__isnull=False,
        ).order_by('-created_at')[:50]

        features = []
        for a in analyses:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [a.longitude, a.latitude],
                },
                'properties': {
                    'id':          a.id,
                    'location':    a.location_name,
                    'risk_level':  a.risk_level,
                    'probability': a.landslide_probability,
                    'date':        a.created_at.strftime('%Y-%m-%d %H:%M'),
                    'has_alert':   hasattr(a, 'public_alert'),
                    'alert_status':a.public_alert.status if hasattr(a, 'public_alert') else None,
                }
            })

        return Response({'type': 'FeatureCollection', 'features': features})