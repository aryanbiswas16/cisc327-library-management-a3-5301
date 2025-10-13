"""
Pytest Configuration File

NOTE: I used AI assistance to create this file because I was struggling 
to figure out how to set up the test environment properly.
"""

import pytest
import sys
import os

# Add parent directory to Python path so tests can import library_service and database
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_folder)

from database import init_database, DATABASE

@pytest.fixture(autouse=True)
def setup_database():
    """Initialize a fresh database before each test."""
    
    # Remove old database file if it exists
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
        except:
            pass
    
    # Create fresh database
    init_database()
    yield
    
    # Clean up after test
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
        except:
            pass
