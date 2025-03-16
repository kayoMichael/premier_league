import pytest
import os
import tempfile
from flask import Flask, g


@pytest.fixture(autouse=True)
def mock_g_temp_state():
    """
    This fixture automatically mocks the Flask g object's temp_state
    attribute for all tests.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, 'test_file.tmp')
        open(temp_file, 'w').close()  # Create empty file

        g.temp_state = {'file_path': temp_file}

        yield


@pytest.fixture
def app_context():
    """Create an application context for tests outside of routes."""
    app = Flask(__name__)
    with app.app_context():
        yield app