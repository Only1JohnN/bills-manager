from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exbox.settings')

app = Celery('exbox')

# Use Redis as the broker
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Add this to explicitly set the broker URL
app.conf.broker_url = 'redis://127.0.0.1:6379/0'