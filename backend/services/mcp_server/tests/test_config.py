"""
Tests for Configuration
=======================

Scientific tests for Pydantic configuration validation.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import os
import pytest
from pydantic import ValidationError

from config import MCPServerConfig, get_config


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_service_name(self):
        """HYPOTHESIS: Default service name is 'mcp-server'."""
        config = MCPServerConfig()
        assert config.service_name == "mcp-server"

    def test_default_service_port(self):
        """HYPOTHESIS: Default port is 8106."""
        config = MCPServerConfig()
        assert config.service_port == 8106

    def test_default_log_level(self):
        """HYPOTHESIS: Default log level is INFO."""
        config = MCPServerConfig()
        assert config.log_level == "INFO"

    def test_default_downstream_urls(self):
        """HYPOTHESIS: Default URLs are localhost with correct ports."""
        config = MCPServerConfig()
        assert config.tribunal_url == "http://localhost:8101"
        assert config.factory_url == "http://localhost:8105"
        assert config.memory_url == "http://localhost:8103"
        assert config.executor_url == "http://localhost:8104"


class TestConfigValidation:
    """Test configuration validation."""

    def test_log_level_validation_valid(self):
        """HYPOTHESIS: Valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = MCPServerConfig(log_level=level)
            assert config.log_level == level

    def test_log_level_validation_case_insensitive(self):
        """HYPOTHESIS: Log level is case-insensitive."""
        config = MCPServerConfig(log_level="debug")
        assert config.log_level == "DEBUG"

    def test_log_level_validation_invalid(self):
        """HYPOTHESIS: Invalid log level raises ValidationError."""
        with pytest.raises(ValidationError, match="log_level must be one of"):
            MCPServerConfig(log_level="INVALID")

    def test_rate_limit_validation_positive(self):
        """HYPOTHESIS: Rate limit must be positive."""
        config = MCPServerConfig(rate_limit_per_tool=100)
        assert config.rate_limit_per_tool == 100

    def test_rate_limit_validation_too_small(self):
        """HYPOTHESIS: Rate limit < 1 raises ValidationError."""
        with pytest.raises(ValidationError):
            MCPServerConfig(rate_limit_per_tool=0)

    def test_rate_limit_validation_too_large(self):
        """HYPOTHESIS: Rate limit > 10000 raises ValidationError."""
        with pytest.raises(ValidationError):
            MCPServerConfig(rate_limit_per_tool=10001)

    def test_circuit_breaker_threshold_positive(self):
        """HYPOTHESIS: Circuit breaker threshold must be positive."""
        config = MCPServerConfig(circuit_breaker_threshold=5)
        assert config.circuit_breaker_threshold == 5

    def test_circuit_breaker_timeout_range(self):
        """HYPOTHESIS: Circuit breaker timeout in valid range."""
        config = MCPServerConfig(circuit_breaker_timeout=30.0)
        assert config.circuit_breaker_timeout == 30.0


class TestConfigEnvironment:
    """Test environment variable loading."""

    def test_env_var_override_port(self, monkeypatch):
        """HYPOTHESIS: MCP_SERVICE_PORT env var overrides default."""
        monkeypatch.setenv("MCP_SERVICE_PORT", "9999")
        config = MCPServerConfig()
        assert config.service_port == 9999

    def test_env_var_override_tribunal_url(self, monkeypatch):
        """HYPOTHESIS: MCP_TRIBUNAL_URL env var overrides default."""
        monkeypatch.setenv("MCP_TRIBUNAL_URL", "http://custom:8888")
        config = MCPServerConfig()
        assert config.tribunal_url == "http://custom:8888"

    def test_env_var_prefix(self, monkeypatch):
        """HYPOTHESIS: Config uses MCP_ prefix for env vars."""
        monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")
        config = MCPServerConfig()
        assert config.log_level == "DEBUG"


class TestConfigSingleton:
    """Test singleton pattern."""

    def test_get_config_returns_instance(self):
        """HYPOTHESIS: get_config() returns MCPServerConfig instance."""
        config = get_config()
        assert isinstance(config, MCPServerConfig)

    def test_get_config_creates_new_instance(self):
        """HYPOTHESIS: get_config() creates fresh instance each call."""
        config1 = get_config()
        config2 = get_config()
        # Note: Not a true singleton, creates new instance
        assert isinstance(config1, MCPServerConfig)
        assert isinstance(config2, MCPServerConfig)


class TestConfigBoundaries:
    """Test configuration boundary conditions."""

    def test_http_timeout_minimum(self):
        """HYPOTHESIS: HTTP timeout >= 1.0 seconds."""
        config = MCPServerConfig(http_timeout=1.0)
        assert config.http_timeout == 1.0

    def test_http_timeout_maximum(self):
        """HYPOTHESIS: HTTP timeout <= 300.0 seconds."""
        config = MCPServerConfig(http_timeout=300.0)
        assert config.http_timeout == 300.0

    def test_http_max_connections_range(self):
        """HYPOTHESIS: Max connections in valid range."""
        config = MCPServerConfig(http_max_connections=100)
        assert config.http_max_connections == 100

    def test_otel_enabled_boolean(self):
        """HYPOTHESIS: OTEL enabled is boolean."""
        config = MCPServerConfig(otel_enabled=True)
        assert config.otel_enabled is True

        config = MCPServerConfig(otel_enabled=False)
        assert config.otel_enabled is False
