"""landslide_project/celery.py"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landslide_project.settings')

app = Celery('landslide_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()