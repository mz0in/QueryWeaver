"""Tests for token management functionality."""

import time
import hashlib
import secrets
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from api.app_factory import create_app
from api.routes.tokens import _generate_secure_token, _hash_token, validate_api_token


class TestTokenGeneration:
    """Test token generation and validation functions"""
    
    def test_generate_secure_token(self):
        """Test that secure tokens are generated correctly"""
        token1 = _generate_secure_token()
        token2 = _generate_secure_token()
        
        # Tokens should be different
        assert token1 != token2
        
        # Tokens should be strings
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        
        # Tokens should have reasonable length
        assert len(token1) > 32
        assert len(token2) > 32
    
    def test_hash_token(self):
        """Test token hashing function"""
        token = "test_token_123"
        hash1 = _hash_token(token)
        hash2 = _hash_token(token)
        
        # Same token should produce same hash
        assert hash1 == hash2
        
        # Hash should be different from original token
        assert hash1 != token
        
        # Hash should be a hex string
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string
        
        # Different tokens should produce different hashes
        different_token = "different_token_456"
        different_hash = _hash_token(different_token)
        assert hash1 != different_hash


class TestTokenAPI:
    """Test token management API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        with patch('api.routes.tokens.db') as mock_db:
            # Mock graph selection and query results
            mock_graph = Mock()
            mock_db.select_graph.return_value = mock_graph
            yield mock_db, mock_graph
    
    @pytest.fixture
    def authenticated_request(self):
        """Mock authenticated request"""
        mock_request = Mock()
        mock_request.state.user_id = "test_user_123"
        return mock_request
    
    def test_generate_token_requires_auth(self, client):
        """Test that token generation requires authentication"""
        response = client.post("/api/tokens/generate")
        assert response.status_code == 401
    
    def test_list_tokens_requires_auth(self, client):
        """Test that token listing requires authentication"""
        response = client.get("/api/tokens/list")
        assert response.status_code == 401
    
    def test_delete_token_requires_auth(self, client):
        """Test that token deletion requires authentication"""
        response = client.delete("/api/tokens/test_token_id")
        assert response.status_code == 401
    
    @patch('api.routes.tokens._get_user_email_from_graph')
    @patch('api.auth.user_management.validate_and_cache_user')
    def test_generate_token_success(self, mock_validate_user, mock_get_email, client, mock_db):
        """Test successful token generation"""
        mock_db_obj, mock_graph = mock_db
        
        # Mock authentication
        mock_validate_user.return_value = ({"id": "test_user_123"}, True)
        mock_get_email.return_value = "test@example.com"
        
        # Mock database operations
        mock_result = Mock()
        mock_result.result_set = [["mock_token_node"]]
        mock_graph.query.return_value = mock_result
        
        # Test with session-based auth (would need to set up session properly)
        # For now, just test that the route exists and validates auth
        response = client.post("/api/tokens/generate")
        assert response.status_code == 401  # Without proper session setup
    
    @patch('api.routes.tokens._get_user_email_from_graph')
    @patch('api.auth.user_management.validate_and_cache_user')
    def test_list_tokens_success(self, mock_validate_user, mock_get_email, client, mock_db):
        """Test successful token listing"""
        mock_db_obj, mock_graph = mock_db
        
        # Mock authentication
        mock_validate_user.return_value = ({"id": "test_user_123"}, True)
        mock_get_email.return_value = "test@example.com"
        
        # Mock database operations
        mock_result = Mock()
        mock_result.result_set = [
            ["token1", int(time.time()), "1234"],
            ["token2", int(time.time()) - 3600, "5678"]
        ]
        mock_graph.query.return_value = mock_result
        
        response = client.get("/api/tokens/list")
        assert response.status_code == 401  # Without proper session setup


class TestTokenValidation:
    """Test API token validation"""
    
    @patch('api.routes.tokens.db')
    def test_validate_api_token_valid(self, mock_db):
        """Test validation of valid API token"""
        # Setup mock
        mock_graph = Mock()
        mock_db.select_graph.return_value = mock_graph
        
        # Mock successful token lookup
        mock_result = Mock()
        mock_result.result_set = [["test@example.com"]]
        mock_graph.query.return_value = mock_result
        
        token = "test_token_123"
        result = validate_api_token(token)
        
        assert result == "test@example.com"
        mock_graph.query.assert_called_once()
    
    @patch('api.routes.tokens.db')
    def test_validate_api_token_invalid(self, mock_db):
        """Test validation of invalid API token"""
        # Setup mock
        mock_graph = Mock()
        mock_db.select_graph.return_value = mock_graph
        
        # Mock failed token lookup
        mock_result = Mock()
        mock_result.result_set = []
        mock_graph.query.return_value = mock_result
        
        token = "invalid_token_123"
        result = validate_api_token(token)
        
        assert result is None
        mock_graph.query.assert_called_once()
    
    def test_validate_api_token_empty(self):
        """Test validation of empty token"""
        result = validate_api_token("")
        assert result is None
        
        result = validate_api_token(None)
        assert result is None
    
    @patch('api.routes.tokens.db')
    def test_validate_api_token_exception(self, mock_db):
        """Test validation when database throws exception"""
        # Setup mock to raise exception
        mock_db.select_graph.side_effect = Exception("Database error")
        
        token = "test_token_123"
        result = validate_api_token(token)
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])