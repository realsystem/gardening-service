"""Tests for security headers middleware.

Verifies that security headers are properly set to protect against:
- XSS attacks
- Clickjacking
- MIME sniffing
- Information disclosure
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.security
class TestSecurityHeaders:
    """Test security headers middleware."""

    def test_security_headers_present_on_api_endpoint(self, client):
        """Test that security headers are present on API responses."""
        response = client.get("/health")

        # X-Content-Type-Options: Prevent MIME sniffing
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

        # X-Frame-Options: Prevent clickjacking
        assert response.headers.get("X-Frame-Options") == "DENY"

        # X-XSS-Protection: Legacy XSS filter
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

        # Content-Security-Policy: Modern XSS prevention
        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src 'none'" in csp
        assert "frame-ancestors 'none'" in csp

        # Referrer-Policy: Prevent information leakage
        assert response.headers.get("Referrer-Policy") == "no-referrer"

        # Permissions-Policy: Disable unnecessary features
        permissions = response.headers.get("Permissions-Policy")
        assert permissions is not None
        assert "geolocation=()" in permissions
        assert "camera=()" in permissions

    def test_hsts_not_present_in_test_environment(self, client):
        """Test that HSTS is not set in test environment (requires HTTPS)."""
        response = client.get("/health")

        # HSTS should only be set in production/staging
        assert "Strict-Transport-Security" not in response.headers

    def test_server_header_removed(self, client):
        """Test that Server header is removed to prevent information disclosure."""
        response = client.get("/health")

        # Server header should be removed
        assert "Server" not in response.headers or response.headers.get("Server") == ""

    def test_security_headers_on_authenticated_endpoint(self, client, user_token):
        """Test security headers on authenticated endpoints."""
        response = client.get("/users/me", headers={"Authorization": f"Bearer {user_token}"})

        # Should have all security headers even on authenticated endpoints
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Content-Security-Policy") is not None

    def test_security_headers_on_error_response(self, client):
        """Test security headers are present even on error responses."""
        # Request non-existent endpoint
        response = client.get("/nonexistent")

        # Security headers should be present on 404 responses
        assert response.status_code == 404
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_csp_blocks_inline_scripts(self, client):
        """Test that CSP policy blocks inline scripts (API-only service)."""
        response = client.get("/health")

        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None

        # default-src 'none' means no scripts allowed at all
        assert "default-src 'none'" in csp

        # No script-src directive means scripts are blocked
        assert "script-src" not in csp

    def test_csp_blocks_frames(self, client):
        """Test that CSP prevents page from being embedded in frames."""
        response = client.get("/health")

        csp = response.headers.get("Content-Security-Policy")
        assert "frame-ancestors 'none'" in csp

    def test_permissions_policy_disables_dangerous_features(self, client):
        """Test that dangerous browser features are disabled."""
        response = client.get("/health")

        permissions = response.headers.get("Permissions-Policy")

        # Geolocation disabled
        assert "geolocation=()" in permissions

        # Camera disabled
        assert "camera=()" in permissions

        # Microphone disabled
        assert "microphone=()" in permissions

        # Payment API disabled
        assert "payment=()" in permissions

        # USB disabled
        assert "usb=()" in permissions


@pytest.mark.security
class TestSecurityHeadersIntegration:
    """Integration tests for security headers with different endpoints."""

    def test_security_headers_on_metrics_endpoint(self, client):
        """Test security headers on metrics endpoint."""
        response = client.get("/metrics")

        # Should have security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_security_headers_on_post_request(self, client, user_token):
        """Test security headers on POST requests."""
        response = client.post(
            "/gardens",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Security Test Garden",
                "garden_type": "outdoor",
                "size_sq_ft": 100
            }
        )

        # Should have security headers on POST responses
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_security_headers_preserved_with_other_headers(self, client):
        """Test that security headers don't interfere with other response headers."""
        response = client.get("/health")

        # Security headers should be present
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

        # Content-Type should still be set correctly
        assert "application/json" in response.headers.get("Content-Type", "")

        # Custom headers should not interfere
        assert response.status_code == 200


@pytest.mark.security
class TestSecurityHeadersDocumentation:
    """Test that security headers are well-documented."""

    def test_headers_match_owasp_recommendations(self, client):
        """Verify headers match OWASP Secure Headers Project recommendations."""
        response = client.get("/health")

        # OWASP recommended headers
        owasp_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Content-Security-Policy",
            "Referrer-Policy",
        ]

        for header in owasp_headers:
            assert response.headers.get(header) is not None, f"Missing OWASP header: {header}"

    def test_headers_provide_defense_in_depth(self, client):
        """Test that multiple headers provide overlapping protection."""
        response = client.get("/health")

        # Multiple clickjacking protections
        assert response.headers.get("X-Frame-Options") == "DENY"
        csp = response.headers.get("Content-Security-Policy")
        assert "frame-ancestors 'none'" in csp

        # These provide overlapping protection for defense-in-depth
