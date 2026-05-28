"""alerts/urls.py"""
from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    # API endpoints
    path('alerts/',              views.PublicAlertListAPI.as_view(),    name='alert-list'),
    path('alerts/area-map/',     views.AreaWarningMapAPI.as_view(),     name='area-warnings'),
    path('safety-instructions/', views.SafetyInstructionsAPI.as_view(), name='safety-instructions'),
    path('emergency-contacts/',  views.EmergencyContactsAPI.as_view(),  name='emergency-contacts'),
    path('shelters/',            views.ShelterListAPI.as_view(),        name='shelter-list'),
    path('shelters/<int:pk>/update/', views.ShelterUpdateAPI.as_view(), name='shelter-update'),

    # Government HTML pages
    path('govt/',                    views.government_dashboard, name='govt-dashboard'),
    path('govt/approve/<int:pk>/',   views.approve_alert,        name='approve-alert'),
    path('govt/reject/<int:pk>/',    views.reject_alert,         name='reject-alert'),
    path('public-alerts/', TemplateView.as_view(template_name='alerts/public_alert.html'), name='public-alerts'),

]