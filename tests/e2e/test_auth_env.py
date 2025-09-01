"""
Test authentication using environment-based configuration.
"""
import os
import pytest
from tests.e2e.pages.home_page import HomePage


@pytest.fixture
def test_auth_env():
    """Set up test authentication environment variables."""
    original_values = {}
    test_env_vars = {
        "ENABLE_TEST_AUTH": "true",
        "APP_ENV": "development", 
        "TEST_USER_EMAIL": "test@example.com",
        "TEST_USER_NAME": "Test User"
    }
    
    # Set test environment variables
    for key, value in test_env_vars.items():
        original_values[key] = os.getenv(key)
        os.environ[key] = value
    
    yield test_env_vars
    
    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


class TestEnvironmentAuth:
    """Test authentication using environment configuration."""

    @pytest.mark.skip(reason="Requires server-side development auth bypass implementation")
    def test_auth_with_dev_bypass(self, page_with_base_url, test_auth_env):
        """Test authentication using development bypass."""
        # This would work if QueryWeaver had a development auth bypass
        home_page = HomePage(page_with_base_url)
        home_page.navigate_to_home()
        
        # With ENABLE_TEST_AUTH=true, the server should skip OAuth
        # and treat the user as authenticated
        
        # Test authenticated features
        assert home_page.is_authenticated()
        
        # Test file upload (should now be available)
        page = page_with_base_url
        file_input = page.query_selector(home_page.FILE_UPLOAD)
        assert file_input is not None, "File upload should be available when authenticated"
