# Tenacity Retry Pattern for MCP Servers

**Last Updated**: 2025-11-02  
**Standard**: MCP Server Retry Logic Best Practices

## Overview

**Tenacity** is a Python library that provides a clean, declarative approach to implementing retry logic for operations that may fail due to transient errors. This document establishes the standard pattern for using tenacity across all MCP server repositories.

## Why Tenacity?

### Problems with Manual Retry Logic

**Before (Manual Retry)**:
```python
for attempt in range(max_retries):
    try:
        result = await client.request(...)
        return result
    except NetworkError:
        if attempt < max_retries - 1:
            await asyncio.sleep(1 * (attempt + 1))  # Basic exponential backoff
raise LastError()
```

**Problems**:
- Verbose and repetitive code
- Hard to configure different retry strategies
- Difficult to test
- Inconsistent across codebase
- No built-in jitter or advanced backoff strategies

### Benefits of Tenacity

**After (Tenacity)**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    reraise=True,
)
async def _make_request(...):
    response = await client.request(...)
    return response
```

**Benefits**:
- Clean, declarative syntax
- Flexible retry strategies (exponential backoff, jitter, fixed delay)
- Conditional retries (retry on specific exceptions only)
- Built-in logging hooks
- Consistent patterns across all repos
- Easy to test and maintain

## Installation

Add to `pyproject.toml`:
```toml
dependencies = [
    "tenacity>=8.2.0",  # Retry logic for network operations and external API calls
]
```

## Standard Retry Pattern

### 1. HTTP/API Client Retries

**When to use**: All HTTP client methods that make external API calls.

**Pattern**:
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),  # Try up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s, 4s, 8s, 10s
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.RequestError)),
    reraise=True,  # Re-raise exception after all retries exhausted
)
async def _make_request(self, endpoint: str, ...) -> Dict[str, Any]:
    """
    Make HTTP request with automatic retry logic.
    
    Retries transient network errors (timeouts, connection failures).
    Does NOT retry HTTP 4xx/5xx errors (permanent failures).
    """
    response = await client.request(...)
    
    # HTTP errors should NOT be retried
    if response.status_code >= 400:
        raise APIError(f"HTTP {response.status_code}: {response.text}")
    
    return response.json()
```

**Key Points**:
- Retry only transient errors (timeouts, connection errors)
- **DO NOT** retry HTTP 4xx/5xx errors (authentication, validation, server errors)
- Use exponential backoff with reasonable min/max values
- Always use `reraise=True` to propagate final exception

### 2. Remote Storage Operations

**When to use**: All remote storage backend methods.

**Pattern**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(
        (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError, aiohttp.ClientError)
    ),
    reraise=True,
)
async def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
    """
    Make authenticated request with automatic retry logic.
    
    Retries transient network errors. Does NOT retry HTTP errors (4xx/5xx).
    """
    async with self.session.request(method, url, **kwargs) as response:
        # HTTP errors raise ClientResponseError - do NOT retry these
        response.raise_for_status()
        return await response.json()
```

### 3. External Service Calls (AI APIs, OCR, etc.)

**When to use**: Calls to external services (OpenAI, OCR services, etc.).

**Pattern**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
async def _generate_metadata(self, metadata, fields: List[str]) -> Dict:
    """
    Generate metadata using AI service with automatic retry logic.
    
    Retries transient service errors (timeouts, temporary unavailability).
    """
    response = await self._ai_client.post(...)
    
    # Service errors (5xx) might be retried, but API errors (4xx) should not
    if response.status_code >= 500:
        raise AIServiceError("Service temporarily unavailable")
    elif response.status_code >= 400:
        raise AIServiceError("Invalid request - do not retry")
    
    return response.json()
```

## Retry Configuration Guidelines

### Stop Conditions

- `stop_after_attempt(3)`: **Standard** - Try up to 3 times (1 initial + 2 retries)
- `stop_after_delay(30)`: For operations with strict time limits
- `stop_after_attempt(5)`: For critical operations that must succeed

### Wait Strategies

- `wait_exponential(multiplier=1, min=2, max=10)`: **Standard** - 2s, 4s, 8s, 10s
- `wait_exponential(multiplier=2, min=1, max=30)`: For longer operations
- `wait_fixed(5)`: For simple fixed delays (use sparingly)

### Retry Conditions

- `retry_if_exception_type((TimeoutError, ConnectionError))`: **Standard** - Retry only transient errors
- `retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))`: For httpx clients
- `retry_if_exception_type((aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError))`: For aiohttp clients
- **DO NOT** retry on authentication errors, validation errors, or HTTP 4xx/5xx

## What to Retry vs. What NOT to Retry

### ✅ Retry (Transient Errors)

- Network timeouts (`httpx.TimeoutException`, `aiohttp.ServerTimeoutError`)
- Connection errors (`httpx.ConnectError`, `aiohttp.ClientConnectionError`)
- Temporary service unavailability (5xx errors in some cases)
- Network-level failures (DNS resolution, connection refused)

### ❌ Do NOT Retry (Permanent Failures)

- Authentication errors (401 Unauthorized)
- Not found errors (404 Not Found)
- Validation errors (400 Bad Request, 422 Unprocessable Entity)
- Authorization errors (403 Forbidden)
- Client errors (4xx status codes)
- Server errors that indicate permanent failures (5xx in some contexts)
- Business logic errors (invalid parameters, missing resources)

## Error Message Guidelines

When using tenacity, provide **AI-friendly error messages** that explain:
1. What failed
2. Why it likely failed
3. What to do about it

**Example**:
```python
except httpx.ConnectError as e:
    raise CalibreAPIError(
        f"Connection failed to {url}. "
        "Possible causes: "
        "1. Calibre Content Server not running - start with 'calibre-server' "
        "2. Incorrect server URL - check CALIBRE_SERVER_URL env var "
        "3. Firewall blocking connection - check firewall settings "
        "4. Wrong port number - default is 8080"
    ) from e
```

## Testing Retry Logic

### Mock Transient Errors

```python
from unittest.mock import patch, AsyncMock
import pytest

@pytest.mark.asyncio
async def test_retry_on_timeout():
    """Test that timeouts trigger retries."""
    with patch("httpx.AsyncClient.request") as mock_request:
        # First two attempts timeout, third succeeds
        mock_request.side_effect = [
            httpx.TimeoutException("Request timed out"),
            httpx.TimeoutException("Request timed out"),
            AsyncMock(status_code=200, json=lambda: {"success": True}),
        ]
        
        result = await client._make_request("test-endpoint")
        assert result == {"success": True}
        assert mock_request.call_count == 3  # Initial + 2 retries
```

### Verify No Retry on Permanent Errors

```python
@pytest.mark.asyncio
async def test_no_retry_on_auth_error():
    """Test that 401 errors are NOT retried."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = AsyncMock(status_code=401, text="Unauthorized")
        mock_request.return_value = mock_response
        
        with pytest.raises(CalibreAPIError, match="Authentication failed"):
            await client._make_request("test-endpoint")
        
        # Should only try once (no retry for auth errors)
        assert mock_request.call_count == 1
```

## Standard Patterns by Use Case

### Pattern 1: HTTP Client (httpx)

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.RequestError)),
    reraise=True,
)
async def _make_request(...) -> Dict[str, Any]:
    # Implementation
```

### Pattern 2: HTTP Client (aiohttp)

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(
        (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError)
    ),
    reraise=True,
)
async def _make_request(...) -> Any:
    # Implementation
```

### Pattern 3: External API Calls

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
async def call_external_api(...) -> Dict[str, Any]:
    # Implementation with proper error handling
```

## Migration Checklist

When migrating existing code to use tenacity:

- [ ] Add `tenacity>=8.2.0` to `pyproject.toml`
- [ ] Remove manual retry loops (`for attempt in range(max_retries)`)
- [ ] Replace `asyncio.sleep()` backoff with `wait_exponential()`
- [ ] Use `retry_if_exception_type()` to specify which errors to retry
- [ ] Ensure HTTP 4xx/5xx errors are NOT retried
- [ ] Add comprehensive docstrings explaining retry behavior
- [ ] Update error messages to be AI-friendly
- [ ] Add tests for retry behavior
- [ ] Verify `reraise=True` is set

## Examples from CalibreMCP

### CalibreAPIClient

See `src/calibre_mcp/calibre_api.py` - `_make_request()` method

### RemoteStorage

See `src/calibre_mcp/storage/remote.py` - `_make_request()` method

### AIEnhancementsTool

See `src/calibre_mcp/tools/advanced_features/ai_enhancements.py` - `_generate_metadata()` method

## References

- [Tenacity GitHub](https://github.com/jd/tenacity)
- [Tenacity Documentation](https://tenacity.readthedocs.io/)
- FastMCP 2.13+ Standards: `docs/mcp-technical/FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md`

## Summary

**Use tenacity for all network operations and external API calls in MCP servers.**

**Standard pattern**:
- 3 retry attempts
- Exponential backoff: 2s, 4s, 8s, 10s
- Retry only transient errors (timeouts, connection errors)
- Do NOT retry permanent errors (authentication, validation, HTTP 4xx/5xx)
- Provide AI-friendly error messages
- Always use `reraise=True`

