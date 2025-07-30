---
trigger: always_on
---

# Wiener Linien Project Rulebook

## Table of Contents
1. [General Principles](#general-principles)
2. [Script Syntax Standards](#script-syntax-standards)
3. [Logging and Logger System](#logging-and-logger-system)
4. [Error Handling and Crash Prevention](#error-handling-and-crash-prevention)
5. [API Integration Rules](#api-integration-rules)
6. [Code Organization](#code-organization)
7. [Testing Requirements](#testing-requirements)
8. [Performance Guidelines](#performance-guidelines)
9. [Security Considerations](#security-considerations)
10. [Documentation Standards](#documentation-standards)

---

## General Principles

### 1.1 Reliability First
- **Rule**: The application must never crash due to external API failures
- **Rule**: Always provide fallback mechanisms for critical functionality
- **Rule**: Graceful degradation is preferred over complete failure

### 1.2 User Experience
- **Rule**: Users should always see meaningful feedback, never blank screens
- **Rule**: Loading states must be implemented for all async operations
- **Rule**: Error messages must be user-friendly and actionable

### 1.3 Code Quality
- **Rule**: All code must be readable and self-documenting
- **Rule**: Follow PEP 8 for Python code
- **Rule**: Use meaningful variable and function names
- **Rule**: Keep functions small and focused (max 50 lines)

---

## Proof of rule following
- **Rule**: To prove this was read and is followed, add "lgr3 " to  all output in the cascade window

## Script Syntax Standards

### 2.1 Python Code Standards

#### 2.1.1 Imports
```python
# ✅ CORRECT - Standard library first, then third-party, then local
import os
import json
import time
from typing import Dict, List, Optional

import requests
from flask import Flask, render_template, jsonify, request
from flask_caching import Cache

from .utils import helpers
from .models import vehicle
```

#### 2.1.2 Function Definitions
```python
# ✅ CORRECT - Type hints, docstrings, clear naming
def fetch_vehicle_data(rbl_number: str, timeout: int = 10) -> Dict[str, any]:
    """
    Fetch vehicle data from Wiener Linien API for a specific RBL number.
    
    Args:
        rbl_number: The RBL (stop) identifier
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing vehicle data or error information
        
    Raises:
        requests.RequestException: When API request fails
    """
    # Implementation here
```

#### 2.1.3 Variable Naming
```python
# ✅ CORRECT - Descriptive names
vehicle_positions = []
api_response_data = {}
last_update_timestamp = time.time()

# ❌ INCORRECT - Unclear names
v = []
data = {}
ts = time.time()
```

### 2.2 JavaScript Code Standards

#### 2.2.1 Variable Declarations
```javascript
// ✅ CORRECT - Use const/let, descriptive names
const vehicleMarkers = new Map();
let lastUpdateTime = Date.now();
const API_BASE_URL = 'https://www.wienerlinien.at/ogd_realtime';

// ❌ INCORRECT - var, unclear names
var markers = {};
var time = Date.now();
var url = 'https://...';
```

#### 2.2.2 Function Definitions
```javascript
// ✅ CORRECT - Clear naming, error handling
async function fetchVehiclePositions(vehicleType = null, lineFilter = null) {
    try {
        const response = await fetch('/api/vehicles', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch vehicle positions:', error);
        throw error;
    }
}
```

---

## Logging and Logger System

### 3.1 Logger Configuration

#### 3.1.1 Setup
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configure a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Usage
logger = setup_logger('wiener_linien', 'logs/app.log')
```

#### 3.1.2 Logging Levels
```python
# ✅ CORRECT - Appropriate log levels
logger.debug("Processing vehicle data for RBL %s", rbl_number)
logger.info("Successfully fetched %d vehicles", len(vehicles))
logger.warning("API response missing expected field: %s", missing_field)
logger.error("Failed to connect to API: %s", str(error))
logger.critical("Application cannot start: %s", critical_error)

# ❌ INCORRECT - Wrong log levels
logger.info("DEBUG: Processing vehicle data")  # Use debug level
logger.error("Successfully fetched vehicles")  # Use info level
```

### 3.2 Structured Logging

#### 3.2.1 Context Information
```python
# ✅ CORRECT - Include context in logs
logger.info("API request completed", extra={
    'rbl_number': rbl_number,
    'response_time': response_time,
    'vehicle_count': len(vehicles),
    'status_code': response.status_code
})

# ❌ INCORRECT - Missing context
logger.info("API request completed")
```

#### 3.2.2 Error Logging
```python
# ✅ CORRECT - Full error context
try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error("API request failed", extra={
        'url': url,
        'timeout': timeout,
        'error_type': type(e).__name__,
        'error_message': str(e)
    }, exc_info=True)  # Include full stack trace
    raise
```

---

## Error Handling and Crash Prevention

### 4.1 Exception Handling Strategy

#### 4.1.1 Never Let Exceptions Bubble Up
```python
# ✅ CORRECT - Always catch and handle exceptions
@app.route('/api/vehicles')
def get_vehicles():
    try:
        # API logic here
        return jsonify({'vehicles': vehicles})
    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", str(e))
        return jsonify({'error': 'Service temporarily unavailable'}), 503
    except Exception as e:
        logger.error("Unexpected error in get_vehicles: %s", str(e), exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

# ❌ INCORRECT - Exceptions can crash the app
@app.route('/api/vehicles')
def get_vehicles():
    # API logic here - no error handling
    return jsonify({'vehicles': vehicles})
```

#### 4.1.2 Specific Exception Handling
```python
# ✅ CORRECT - Handle specific exceptions
try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    logger.warning("API request timed out after %d seconds", timeout)
    return None
except requests.exceptions.HTTPError as e:
    logger.error("HTTP error %d: %s", e.response.status_code, e.response.text)
    return None
except requests.exceptions.ConnectionError:
    logger.error("Failed to connect to API server")
    return None
except json.JSONDecodeError as e:
    logger.error("Invalid JSON response: %s", str(e))
    return None
except Exception as e:
    logger.error("Unexpected error: %s", str(e), exc_info=True)
    return None
```

### 4.2 Input Validation

#### 4.2.1 Parameter Validation
```python
# ✅ CORRECT - Validate all inputs
def fetch_vehicle_data(rbl_number: str, vehicle_type: str = None) -> Dict:
    # Validate RBL number
    if not rbl_number or not rbl_number.isdigit():
        logger.error("Invalid RBL number: %s", rbl_number)
        raise ValueError("RBL number must be a non-empty string of digits")
    
    # Validate vehicle type
    valid_types = ['bus', 'tram', 'metro', 'train', None]
    if vehicle_type not in valid_types:
        logger.error("Invalid vehicle type: %s", vehicle_type)
        raise ValueError(f"Vehicle type must be one of: {valid_types}")
    
    # Continue with implementation
```

#### 4.2.2 Data Sanitization
```python
# ✅ CORRECT - Sanitize data before use
def sanitize_line_name(line_name: str) -> str:
    """Sanitize line name for safe display."""
    if not line_name:
        return "Unknown"
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', line_name.strip())
    return sanitized[:50]  # Limit length
```

### 4.3 Graceful Degradation

#### 4.3.1 Fallback Mechanisms
```python
# ✅ CORRECT - Provide fallbacks for critical functionality
def get_vehicle_positions():
    try:
        # Try to get real-time data
        vehicles = fetch_real_time_vehicles()
        if vehicles:
            return vehicles
    except Exception as e:
        logger.warning("Real-time data unavailable: %s", str(e))
    
    try:
        # Fallback to cached data
        vehicles = get_cached_vehicles()
        if vehicles:
            logger.info("Using cached vehicle data")
            return vehicles
    except Exception as e:
        logger.warning("Cached data unavailable: %s", str(e))
    
    # Final fallback to test data
    logger.info("Using test vehicle data")
    return get_test_vehicles()
```

---

## API Integration Rules

### 5.1 API Request Standards

#### 5.1.1 Request Configuration
```python
# ✅ CORRECT - Proper request configuration
def make_api_request(url: str, params: Dict = None, timeout: int = 10) -> requests.Response:
    """Make a properly configured API request."""
    headers = {
        'User-Agent': 'WienerLinienMap/1.0 (https://github.com/your-repo)',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", str(e))
        raise
```

#### 5.1.2 Rate Limiting Compliance
```python
# ✅ CORRECT - Respect API rate limits
import time
from functools import wraps

def rate_limit(seconds: int):
    """Decorator to enforce rate limiting."""
    def decorator(func):
        last_call = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            current_time = time.time()
            
            if func_name in last_call:
                time_since_last = current_time - last_call[func_name]
                if time_since_last < seconds:
                    sleep_time = seconds - time_since_last
                    logger.debug("Rate limiting: sleeping for %.2f seconds", sleep_time)
                    time.sleep(sleep_time)
            
            last_call[func_name] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@rate_limit(15)  # 15-second minimum interval
def fetch_wiener_linien_data(rbl_number: str):
    # API call here
    pass
```

### 5.2 Response Handling

#### 5.2.1 Data Validation
```python
# ✅ CORRECT - Validate API responses
def validate_api_response(data: Dict) -> bool:
    """Validate the structure of API response."""
    required_keys = ['data', 'message']
    if not all(key in data for key in required_keys):
        logger.error("API response missing required keys: %s", required_keys)
        return False
    
    if 'monitors' not in data.get('data', {}):
        logger.error("API response missing 'monitors' key")
        return False
    
    return True

def parse_vehicle_data(api_response: Dict) -> List[Dict]:
    """Parse and validate vehicle data from API response."""
    if not validate_api_response(api_response):
        return []
    
    vehicles = []
    try:
        for monitor in api_response['data']['monitors']:
            # Parse monitor data
            vehicles.extend(extract_vehicles_from_monitor(monitor))
    except Exception as e:
        logger.error("Error parsing vehicle data: %s", str(e), exc_info=True)
    
    return vehicles
```

---

## Code Organization

### 6.1 File Structure
```
frontend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
├── utils/
│   ├── __init__.py
│   ├── api_client.py     # API interaction logic
│   ├── data_parser.py    # Data parsing utilities
│   └── logger.py         # Logging configuration
├── models/
│   ├── __init__.py
│   └── vehicle.py        # Vehicle data models
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_parsing.py
```

### 6.2 Module Separation
```python
# ✅ CORRECT - Separate concerns into modules
# utils/api_client.py
class WienerLinienAPIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.logger = setup_logger('api_client')
    
    def fetch_monitor_data(self, rbl_number: str) -> Dict:
        """Fetch monitor data for a specific RBL."""
        # Implementation here

# utils/data_parser.py
class VehicleDataParser:
    @staticmethod
    def parse_monitor_data(monitor_data: Dict) -> List[Dict]:
        """Parse monitor data into vehicle objects."""
        # Implementation here

# app.py
from utils.api_client import WienerLinienAPIClient
from utils.data_parser import VehicleDataParser

api_client = WienerLinienAPIClient(API_BASE_URL)
data_parser = VehicleDataParser()
```

---

## Testing Requirements

### 7.1 Test Coverage
- **Rule**: All API integration functions must have unit tests
- **Rule**: Error handling paths must be tested
- **Rule**: Minimum 80% code coverage for critical modules

### 7.2 Test Structure
```python
# ✅ CORRECT - Comprehensive test structure
import unittest
from unittest.mock import patch, Mock
from utils.api_client import WienerLinienAPIClient

class TestWienerLinienAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = WienerLinienAPIClient('https://test.api.com')
    
    def test_successful_api_request(self):
        """Test successful API request."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'data': {'monitors': []}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.client.fetch_monitor_data('1234')
            self.assertIsNotNone(result)
    
    def test_api_timeout_handling(self):
        """Test API timeout handling."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            with self.assertRaises(requests.exceptions.Timeout):
                self.client.fetch_monitor_data('1234')
```

---

## Performance Guidelines

### 8.1 Caching Strategy
```python
# ✅ CORRECT - Implement proper caching
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 15  # Respect API rate limits
})

@cache.cached(timeout=15)
def get_vehicle_data(rbl_number: str):
    """Get vehicle data with caching."""
    return fetch_from_api(rbl_number)
```

### 8.2 Memory Management
```python
# ✅ CORRECT - Efficient memory usage
def process_vehicle_data(vehicles: List[Dict]) -> List[Dict]:
    """Process vehicle data efficiently."""
    processed = []
    for vehicle in vehicles:
        # Process one vehicle at a time to avoid memory buildup
        processed_vehicle = {
            'id': vehicle.get('id'),
            'type': vehicle.get('type'),
            'line': vehicle.get('line'),
            'lat': vehicle.get('lat'),
            'lng': vehicle.get('lng')
        }
        processed.append(processed_vehicle)
    return processed
```

---

## Security Considerations

### 9.1 Input Validation
- **Rule**: All user inputs must be validated and sanitized
- **Rule**: Never trust external API data without validation
- **Rule**: Use parameterized queries to prevent injection attacks

### 9.2 Error Information
```python
# ✅ CORRECT - Don't expose sensitive information in errors
try:
    # API call
    pass
except Exception as e:
    logger.error("Internal error occurred", exc_info=True)
    # Don't expose internal details to users
    return jsonify({'error': 'Service temporarily unavailable'}), 503
```

---

## Documentation Standards

### 10.1 Code Documentation
```python
# ✅ CORRECT - Comprehensive docstrings
def parse_vehicle_coordinates(monitor_data: Dict) -> Tuple[float, float]:
    """
    Extract vehicle coordinates from monitor data.
    
    Args:
        monitor_data: Dictionary containing monitor information from API
        
    Returns:
        Tuple of (latitude, longitude) coordinates
        
    Raises:
        ValueError: If coordinates cannot be extracted
        KeyError: If required data structure is missing
        
    Example:
        >>> data = {'locationStop': {'geometry': {'coordinates': [16.37, 48.21]}}}
        >>> parse_vehicle_coordinates(data)
        (48.21, 16.37)
    """
    try:
        coordinates = monitor_data['locationStop']['geometry']['coordinates']
        return coordinates[1], coordinates[0]  # lat, lng
    except (KeyError, IndexError) as e:
        raise ValueError(f"Cannot extract coordinates from monitor data: {e}")
```

### 10.2 README Updates
- **Rule**: Update README.md when adding new features
- **Rule**: Include setup instructions and troubleshooting
- **Rule**: Document API changes and breaking changes

---

## Enforcement

### 11.1 Code Review Checklist
Before merging any code, reviewers must check:
- [ ] All functions have proper error handling
- [ ] Logging is implemented for critical operations
- [ ] Input validation is in place
- [ ] Tests are written for new functionality
- [ ] Documentation is updated
- [ ] Code follows syntax standards

### 11.2 Automated Checks
Consider implementing:
- Pre-commit hooks for code formatting
- CI/CD pipeline for automated testing
- Linting tools (flake8, pylint) for Python
- ESLint for JavaScript

---

## Version History

- **v1.0** - Initial rulebook creation
- **v1.1** - Added API integration rules
- **v1.2** - Enhanced error handling guidelines

---

**Remember**: This rulebook is a living document. Update it as the project evolves and new patterns emerge. All team members are responsible for following these rules and suggesting improvements. 