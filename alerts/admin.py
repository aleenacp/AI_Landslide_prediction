"""alerts/admin.py"""
from django.contrib import admin
from .models import (PublicAlert, GovernmentApproval, SafetyInstruction,
                     EmergencyContact, Shelter)


@admin.register(PublicAlert)
class PublicAlertAdmin(admin.ModelAdmin):
    list_display  = ['id', 'severity', 'status', 'affected_district',
                     'sms_sent_count', 'email_sent_count', 'created_at']
    list_filter   = ['severity', 'status']
    search_fields = ['affected_district', 'affected_ward']
    readonly_fields = ['created_at', 'sent_at', 'sms_sent_count',
                       'email_sent_count', 'push_sent_count']


@admin.register(GovernmentApproval)
class GovernmentApprovalAdmin(admin.ModelAdmin):
    list_display = ['id', 'alert', 'officer', 'action', 'timestamp']
    list_filter  = ['action']


@admin.register(SafetyInstruction)
class SafetyInstructionAdmin(admin.ModelAdmin):
    list_display  = ['title_en', 'severity', 'category', 'icon', 'is_active', 'order']
    list_filter   = ['severity', 'category', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'phone', 'district', 'is_active']
    list_filter   = ['category', 'district', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'phone', 'district']


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display  = ['name', 'district', 'capacity', 'current_occupancy',
                     'is_open', 'has_food', 'has_medical', 'last_updated']
    list_filter   = ['district', 'is_open', 'has_food', 'has_medical']
    list_editable = ['is_open', 'current_occupancy']
    search_fields = ['name', 'district', 'address']