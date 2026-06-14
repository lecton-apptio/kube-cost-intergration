"""Tests for kubecost_integration.core module."""

import json
from unittest.mock import Mock, patch

import pytest

from kubecost_integration.core import (
    CloudabilityClient,
    NamespaceCost,
    build_curl_command,
    load_env_file,
    redact_token,
)


class TestRedactToken:
    """Tests for redact_token function."""

    def test_redact_none(self):
        """Test redacting None value."""
        assert redact_token(None) is None

    def test_redact_empty(self):
        """Test redacting empty string."""
        assert redact_token("") == ""

    def test_redact_short(self):
        """Test redacting short token."""
        assert redact_token("abc") == "***"
        assert redact_token("abcdefgh") == "********"

    def test_redact_long(self):
        """Test redacting long token."""
        token = "01ae074042d56d1d275dab7c383551120a10df82"
        result = redact_token(token)
        assert result == "01ae...df82"
        assert len(result) == 11


class TestBuildCurlCommand:
    """Tests for build_curl_command function."""

    def test_basic_curl(self):
        """Test building basic curl command."""
        url = "https://api.example.com/test"
        headers = {"Accept": "application/json"}
        params = {"key": "value"}
        
        result = build_curl_command(url, headers, params)
        assert "curl -sS -X GET" in result
        assert url in result
        assert "key=value" in result

    def test_redact_token_in_headers(self):
        """Test that tokens in headers are redacted."""
        url = "https://api.example.com/test"
        headers = {"apptio-opentoken": "secret123456789"}
        params = {}
        
        result = build_curl_command(url, headers, params)
        assert "secret123456789" not in result
        assert "secr...6789" in result


class TestNamespaceCost:
    """Tests for NamespaceCost dataclass."""

    def test_create_basic(self):
        """Test creating basic NamespaceCost."""
        cost = NamespaceCost(
            namespace="test",
            start_date="2026-05-01",
            end_date="2026-06-01",
            total_cost=100.50
        )
        assert cost.namespace == "test"
        assert cost.total_cost == 100.50
        assert cost.currency == "USD"
        assert cost.breakdown == []

    def test_create_with_breakdown(self):
        """Test creating NamespaceCost with breakdown."""
        breakdown = [{"service": "EC2", "cost": 50.0}]
        cost = NamespaceCost(
            namespace="test",
            start_date="2026-05-01",
            end_date="2026-06-01",
            total_cost=50.0,
            breakdown=breakdown
        )
        assert cost.breakdown == breakdown


class TestCloudabilityClient:
    """Tests for CloudabilityClient class."""

    def test_init(self):
        """Test client initialization."""
        client = CloudabilityClient(
            apptio_opentoken="test-token",
            environment_id="test-env-id"
        )
        assert client.apptio_opentoken == "test-token"
        assert client.environment_id == "test-env-id"
        assert client.api_url == "https://api.cloudability.com"

    def test_init_custom_url(self):
        """Test client initialization with custom URL."""
        client = CloudabilityClient(
            apptio_opentoken="test-token",
            environment_id="test-env-id",
            api_url="https://custom.api.com"
        )
        assert client.api_url == "https://custom.api.com"

    def test_build_headers(self):
        """Test building request headers."""
        client = CloudabilityClient(
            apptio_opentoken="test-token",
            environment_id="test-env-id"
        )
        headers = client._build_headers()
        
        assert headers["apptio-opentoken"] == "test-token"
        assert headers["apptio-environmentid"] == "test-env-id"
        assert headers["x-cldy-feature"] == "truecost_explorer"

    def test_get_config_summary(self):
        """Test getting configuration summary."""
        client = CloudabilityClient(
            apptio_opentoken="test-token-123456789",
            environment_id="test-env-id"
        )
        summary = client.get_config_summary()
        
        assert summary["environment_id"] == "test-env-id"
        assert summary["opentoken_present"] is True
        assert "test-token-123456789" not in str(summary)

    @patch("kubecost_integration.core.request_json")
    def test_get_namespace_costs_success(self, mock_request):
        """Test successful namespace cost retrieval."""
        # Mock API response
        mock_response = {
            "aggregates": [{"values": ["4.139965"]}],
            "count": 2,
            "rows": [
                {
                    "dimensions": ["On-Demand", "AWS EC2", "Usage", "Data Transfer"],
                    "metrics": [{"sum": "1.355011", "count": "3012"}]
                },
                {
                    "dimensions": ["Savings Plan", "AWS EC2", "Usage", "Instance Usage"],
                    "metrics": [{"sum": "2.784954", "count": "43"}]
                }
            ]
        }
        mock_request.return_value = (200, mock_response)
        
        client = CloudabilityClient(
            apptio_opentoken="test-token",
            environment_id="test-env-id"
        )
        
        result = client.get_namespace_costs(
            namespace="pythia",
            start_date="2026-05-15",
            end_date="2026-06-14"
        )
        
        assert isinstance(result, NamespaceCost)
        assert result.namespace == "pythia"
        assert result.total_cost == 4.139965
        assert result.row_count == 2
        assert result.breakdown is not None
        assert len(result.breakdown) == 2
        assert result.breakdown[0]["service_name"] == "AWS EC2"

    @patch("kubecost_integration.core.request_json")
    def test_get_namespace_costs_default_dates(self, mock_request):
        """Test namespace cost retrieval with default dates."""
        mock_response = {
            "aggregates": [{"values": ["10.0"]}],
            "count": 0,
            "rows": []
        }
        mock_request.return_value = (200, mock_response)
        
        client = CloudabilityClient(
            apptio_opentoken="test-token",
            environment_id="test-env-id"
        )
        
        result = client.get_namespace_costs(namespace="test")
        
        assert result.namespace == "test"
        assert result.total_cost == 10.0
        # Verify dates were set (should be last 30 days)
        assert result.start_date is not None
        assert result.end_date is not None


class TestLoadEnvFile:
    """Tests for load_env_file function."""

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading non-existent file."""
        # Should not raise an error
        load_env_file(str(tmp_path / "nonexistent.env"))

    def test_load_env_file(self, tmp_path, monkeypatch):
        """Test loading environment variables from file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TEST_VAR1=value1\n"
            "TEST_VAR2=value2\n"
            "# Comment line\n"
            "TEST_VAR3=value3\n"
        )
        
        # Clear any existing env vars
        monkeypatch.delenv("TEST_VAR1", raising=False)
        monkeypatch.delenv("TEST_VAR2", raising=False)
        monkeypatch.delenv("TEST_VAR3", raising=False)
        
        load_env_file(str(env_file))
        
        import os
        assert os.getenv("TEST_VAR1") == "value1"
        assert os.getenv("TEST_VAR2") == "value2"
        assert os.getenv("TEST_VAR3") == "value3"


# Made with Bob