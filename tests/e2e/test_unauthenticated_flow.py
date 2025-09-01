"""
Test the user experience for unauthenticated users.
"""
import pytest
from tests.e2e.pages.home_page import HomePage


class TestUnauthenticatedFlow:
    """Test what unauthenticated users can see and do."""

    def test_landing_page_loads(self, page_with_base_url):
        """Test that the landing page loads for unauthenticated users."""
        home_page = HomePage(page_with_base_url)
        home_page.navigate_to_home()
        
        # Should show login options
        page = page_with_base_url
        assert "QueryWeaver" in page.title()
        
        # Should have login buttons visible
        google_login = page.query_selector("a[href*='google']")
        github_login = page.query_selector("a[href*='github']")
        
        # At least one login option should be available
        assert google_login or github_login, "Login options should be visible"

    def test_authentication_prompts(self, page_with_base_url):
        """Test that users are prompted to authenticate when needed."""
        home_page = HomePage(page_with_base_url)
        home_page.navigate_to_home()
        
        page = page_with_base_url
        
        # Message input should show authentication prompt
        message_input = page.query_selector("#message-input")
        if message_input:
            placeholder = message_input.get_attribute("placeholder")
            assert "log in" in placeholder.lower() or "authenticate" in placeholder.lower()
        
        # File upload should not be accessible
        file_input = page.query_selector("#schema-upload")
        if file_input:
            assert not file_input.is_visible(), "File upload should not be visible to unauthenticated users"

    def test_login_button_redirects(self, page_with_base_url):
        """Test that login buttons work and redirect to OAuth providers."""
        home_page = HomePage(page_with_base_url)
        home_page.navigate_to_home()
        
        page = page_with_base_url
        
        # Test Google login redirect
        google_login = page.query_selector("a[href*='google']")
        if google_login and google_login.is_visible():
            # Get the href to verify it points to OAuth
            href = google_login.get_attribute("href")
            assert "/login/google" in href
            
            # Click and verify redirect (but don't complete OAuth)
            google_login.click()
            page.wait_for_timeout(1000)
            
            # Should redirect to OAuth provider or show error
            current_url = page.url
            assert "google" in current_url or "oauth" in current_url or "error" in current_url

    def test_restricted_features_blocked(self, page_with_base_url):
        """Test that features requiring auth are properly blocked."""
        page = page_with_base_url
        
        # Try to access API endpoints that require auth
        response = page.request.get(f"{page.app_url}/graphs")
        assert response.status == 401, "Graphs endpoint should require authentication"
        
        response = page.request.post(f"{page.app_url}/graphs", data={})
        assert response.status == 401, "Graph creation should require authentication"
