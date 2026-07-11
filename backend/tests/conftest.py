"""
Shared pytest fixtures for the backend test suite.

Add project-wide fixtures here; app-specific fixtures go in
tests/<app>/conftest.py.
"""

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    """Use a single test database across the session."""
    pass
