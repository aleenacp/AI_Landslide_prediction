"""
alerts/models.py
New models: PublicAlert, GovernmentApproval, SafetyInstruction,
            EmergencyContact, Shelter
"""
from django.db import models
from django.contrib.auth.models import User
from predictions.models import LandslideAnalysis


# ── 1. PUBLIC ALERT ─────────────────────────────────────────────────────────
class PublicAlert(models.Model):
    SEVERITY_CHOICES = [
        ('watch',    'Watch'),
        ('warning',  'Warning'),
        ('evacuate', 'Evacuate'),
        ('all_clear','All Clear'),
    ]
    STATUS_CHOICES = [
        ('pending',  'Pending Govt Approval'),
        ('approved', 'Approved & Sent'),
        ('rejected', 'Rejected'),
    ]

    analysis         = models.OneToOneField(
                           LandslideAnalysis, on_delete=models.CASCADE,
                           related_name='public_alert')
    severity         = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                        default='pending')
    affected_district= models.CharField(max_length=255, blank=True)
    affected_ward    = models.CharField(max_length=255, blank=True)
    affected_area_km2= models.FloatField(null=True, blank=True)
    estimated_population = models.IntegerField(null=True, blank=True)
    message_english  = models.TextField(blank=True)
    message_malayalam= models.TextField(blank=True)
    sms_sent_count   = models.IntegerField(default=0)
    email_sent_count = models.IntegerField(default=0)
    push_sent_count  = models.IntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    sent_at          = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert #{self.pk} — {self.severity} — {self.status}"


# ── 2. GOVERNMENT APPROVAL ──────────────────────────────────────────────────
class GovernmentApproval(models.Model):
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('override', 'Override (Force Send)'),
    ]

    alert      = models.ForeignKey(PublicAlert, on_delete=models.CASCADE,
                                   related_name='approvals')
    officer    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    notes      = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} by {self.officer} at {self.timestamp}"


# ── 3. SAFETY INSTRUCTION ───────────────────────────────────────────────────
class SafetyInstruction(models.Model):
    SEVERITY_CHOICES = [
        ('all',      'All Levels'),
        ('moderate', 'Moderate+'),
        ('high',     'High+'),
        ('critical', 'Critical Only'),
    ]
    CATEGORY_CHOICES = [
        ('before',  'Before Landslide'),
        ('during',  'During Landslide'),
        ('after',   'After Landslide'),
        ('general', 'General Safety'),
    ]

    severity    = models.CharField(max_length=20, choices=SEVERITY_CHOICES,
                                   default='all')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES,
                                   default='general')
    title_en    = models.CharField(max_length=255)
    title_ml    = models.CharField(max_length=255, blank=True,
                                   verbose_name='Title (Malayalam)')
    body_en     = models.TextField()
    body_ml     = models.TextField(blank=True,
                                   verbose_name='Body (Malayalam)')
    icon        = models.CharField(max_length=10, default='⚠️',
                                   help_text='Emoji icon')
    order       = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'category']

    def __str__(self):
        return self.title_en


# ── 4. EMERGENCY CONTACT ────────────────────────────────────────────────────
class EmergencyContact(models.Model):
    CATEGORY_CHOICES = [
        ('ndrf',       'NDRF / Rescue'),
        ('police',     'Police'),
        ('fire',       'Fire & Rescue'),
        ('medical',    'Hospital / Medical'),
        ('government', 'District Collectorate'),
        ('helpline',   'General Helpline'),
        ('other',      'Other'),
    ]

    name      = models.CharField(max_length=255)
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    phone     = models.CharField(max_length=20)
    alt_phone = models.CharField(max_length=20, blank=True)
    email     = models.EmailField(blank=True)
    district  = models.CharField(max_length=100, blank=True,
                                 help_text='Leave blank for statewide')
    address   = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order     = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category}) — {self.phone}"


# ── 5. SHELTER ──────────────────────────────────────────────────────────────
class Shelter(models.Model):
    name         = models.CharField(max_length=255)
    address      = models.TextField()
    district     = models.CharField(max_length=100)
    latitude     = models.FloatField()
    longitude    = models.FloatField()
    capacity     = models.IntegerField(help_text='Max people')
    current_occupancy = models.IntegerField(default=0)
    is_open      = models.BooleanField(default=False)
    has_food     = models.BooleanField(default=False)
    has_medical  = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_phone= models.CharField(max_length=20, blank=True)
    notes        = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district', 'name']

    def __str__(self):
        status = "OPEN" if self.is_open else "CLOSED"
        return f"{self.name} — {self.district} [{status}] {self.current_occupancy}/{self.capacity}"

    @property
    def available_capacity(self):
        return max(0, self.capacity - self.current_occupancy)

    @property
    def occupancy_percent(self):
        if self.capacity == 0:
            return 0
        return round((self.current_occupancy / self.capacity) * 100, 1)