"""
Makes the Celery app available when Django starts.
Workers are launched with: celery -A core worker ...
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
