"""
Shared pytest fixtures for the backend test suite.

Environment variables set here configure Celery for eager-mode testing
before Django and Celery are imported via core.celery.
"""

import os

os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True"
os.environ["CELERY_TASK_EAGER_PROPAGATES"] = "True"
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
