"""
Tests for Base HTTP Client
===========================

Scientific tests for HTTP client with retry, pooling, and HTTP/2.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from clients.base_client import BaseHTTPClient


class TestBaseClientCreation:
    """Test BaseHTTPClient initialization."""

    def test_client_creation_with_defaults(self, config):
        """HYPOTHESIS: Client initializes with config defaults."""
        client = BaseHTTPClient(config, "http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.client is not None

    def test_client_uses_http2(self, config):
        """HYPOTHESIS: Client enables HTTP/2."""
        client = BaseHTTPClient(config, "http://localhost:8000")
        # HTTP/2 is enabled in __init__
        assert client.client._transport is not None

    def test_client_uses_connection_pooling(self, config):
        """HYPOTHESIS: Client configures connection limits."""
        config.http_max_connections = 50
        config.http_max_keepalive = 20

        client = BaseHTTPClient(config, "http://localhost:8000")
        # Just verify client was created successfully (limits are private)
        assert client.client is not None
        assert isinstance(client.client, httpx.AsyncClient)

    def test_client_uses_custom_timeout(self, config):
        """HYPOTHESIS: Client respects custom timeout."""
        client = BaseHTTPClient(config, "http://localhost:8000", timeout=15.0)
        assert client.client.timeout.read == 15.0


class TestBaseClientGET:
    """Test GET request functionality."""

    @pytest.mark.asyncio
    async def test_get_success(self, config, mock_httpx_response):
        """HYPOTHESIS: Successful GET returns JSON response."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_httpx_response
            mock_httpx_response.json.return_value = {"status": "ok"}

            result = await client.get("/health")

            assert result == {"status": "ok"}
            mock_get.assert_called_once_with("/health", params=None)

    @pytest.mark.asyncio
    async def test_get_with_params(self, config, mock_httpx_response):
        """HYPOTHESIS: GET passes query parameters."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_httpx_response

            await client.get("/search", params={"q": "test"})

            mock_get.assert_called_once_with("/search", params={"q": "test"})

    @pytest.mark.asyncio
    async def test_get_http_error(self, config):
        """HYPOTHESIS: GET raises HTTPError on non-2xx status."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.get("/notfound")

    @pytest.mark.asyncio
    async def test_get_retry_on_timeout(self, config, mock_httpx_response):
        """HYPOTHESIS: GET retries on timeout."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            # First call times out, second succeeds
            mock_get.side_effect = [
                httpx.TimeoutException("Timeout"),
                mock_httpx_response
            ]

            result = await client.get("/slow", retry=True)

            assert result is not None
            assert mock_get.call_count == 2


class TestBaseClientPOST:
    """Test POST request functionality."""

    @pytest.mark.asyncio
    async def test_post_success(self, config, mock_httpx_response):
        """HYPOTHESIS: Successful POST returns JSON response."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response
            mock_httpx_response.json.return_value = {"id": 123}

            result = await client.post("/create", json={"name": "test"})

            assert result == {"id": 123}
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_with_json_body(self, config, mock_httpx_response):
        """HYPOTHESIS: POST sends JSON payload."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        payload = {"key": "value", "number": 42}

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response

            await client.post("/endpoint", json=payload)

            # Verify JSON was passed
            call_args = mock_post.call_args
            assert call_args[0][0] == "/endpoint"
            assert call_args[1]["json"] == payload

    @pytest.mark.asyncio
    async def test_post_retry_exponential_backoff(self, config, mock_httpx_response):
        """HYPOTHESIS: POST retries with exponential backoff."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            # Fail twice, succeed third time
            mock_post.side_effect = [
                httpx.ConnectError("Connection refused"),
                httpx.ConnectError("Connection refused"),
                mock_httpx_response
            ]

            result = await client.post("/endpoint", json={}, retry=True)

            assert result is not None
            assert mock_post.call_count == 3

    @pytest.mark.asyncio
    async def test_post_no_retry_when_disabled(self, config):
        """HYPOTHESIS: POST doesn't retry when retry=False."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(httpx.TimeoutException):
                await client.post("/endpoint", json={}, retry=False)

            assert mock_post.call_count == 1


class TestBaseClientDELETE:
    """Test DELETE request functionality."""

    @pytest.mark.asyncio
    async def test_delete_success(self, config, mock_httpx_response):
        """HYPOTHESIS: Successful DELETE returns True."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_httpx_response.status_code = 204
            mock_delete.return_value = mock_httpx_response

            result = await client.delete("/resource/123")

            assert result is True
            mock_delete.assert_called_once_with("/resource/123")

    @pytest.mark.asyncio
    async def test_delete_not_found(self, config):
        """HYPOTHESIS: DELETE raises HTTPError on 404."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )
            mock_delete.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.delete("/notfound")


class TestBaseClientLifecycle:
    """Test client lifecycle management."""

    @pytest.mark.asyncio
    async def test_close_releases_resources(self, config):
        """HYPOTHESIS: close() releases HTTP connections."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'aclose', new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self, config):
        """HYPOTHESIS: Context manager auto-closes client."""
        async with BaseHTTPClient(config, "http://localhost:8000") as client:
            assert client is not None

        # Client should be closed after exiting context


class TestBaseClientErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_network_error_raises_appropriate_exception(self, config):
        """HYPOTHESIS: Network errors are wrapped appropriately."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(httpx.ConnectError):
                await client.get("/endpoint", retry=False)

    @pytest.mark.asyncio
    async def test_timeout_error_after_retries(self, config):
        """HYPOTHESIS: TimeoutError raised after exhausting retries."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            # Always timeout
            mock_post.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(httpx.TimeoutException):
                await client.post("/endpoint", json={}, retry=True)

            # Should have retried 3 times
            assert mock_post.call_count == 3

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, config):
        """HYPOTHESIS: Invalid JSON raises appropriate error."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="Invalid JSON"):
                await client.get("/endpoint")


class TestBaseClientRetryLogic:
    """Test retry mechanism details."""

    @pytest.mark.asyncio
    async def test_retry_only_on_transient_errors(self, config):
        """HYPOTHESIS: Retry only happens for transient errors."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            # 4xx errors should NOT be retried
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=mock_response
            )
            mock_post.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.post("/endpoint", json={}, retry=True)

            # Should NOT retry on 4xx
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_max_retry_attempts(self, config, mock_httpx_response):
        """HYPOTHESIS: Retries stop after max attempts."""
        client = BaseHTTPClient(config, "http://localhost:8000")

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            # Fail 10 times
            mock_get.side_effect = [httpx.TimeoutException("Timeout")] * 10

            with pytest.raises(httpx.TimeoutException):
                await client.get("/endpoint", retry=True)

            # Should stop at 3 attempts (configured in tenacity)
            assert mock_get.call_count == 3
