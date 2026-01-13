import pytest
import frontend.app as app_module
from frontend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    # Patch backend URL in the module
    original_url = app_module.BACKEND_URL
    app_module.BACKEND_URL = 'http://mock-backend'
    
    with app.test_client() as client:
        yield client
        
    app_module.BACKEND_URL = original_url
