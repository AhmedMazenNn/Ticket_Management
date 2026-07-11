"""Celery application for the Ticket Management project."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("ticket_management")

# Read all Celery config from Django settings (CELERY_ namespace).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all INSTALLED_APPS.
app.autodiscover_tasks()
