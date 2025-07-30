# Logging System

## Overview

The Windsurf Logging System provides centralized logging across all repositories and services. Allogs are stored in the `.windsurf/logs` directory and follow a standardized format.

## Key Features

- **Centralized Storage**: Allogs are stored in a centralocation
- **Standardized Format**: Consistent log format across all services
- **Automatic Rotation**: Logs are automatically rotated and compressed
- **Cross-Service Correlation**: Trace requests across multiple services
- **Security**: Sensitive information is automatically redacted

## Log File Structure

```
.windsurf/logs/
├── {service_name}_{timestamp}.log       # Main log files
├── {service_name}_error_{timestamp}.log  # Error logs
└── archive/                             # Compressed logs
    └── {year}-{month}-{service_name}.tar.gz
```

## Log Format

```
[YYYY-MM-DD HH:MM:SS,SSS] [SERVICE] [LEVEL] [REQUEST_ID] - Message
```

Example:
```
[2025-06-23 15:30:45,123] [API] [INFO] [req-abc123] - Request received from 192.168.1.1
```

## Log Levels

| Level    | Description                          |
|----------|--------------------------------------|
| DEBUG    | Detailedebug information           |
| INFO     | General operational messages         |
| WARNING  | Indicates potential issues           |
| ERROR    | Errors that don't stop execution     |
| CRITICAL | System is unusable                   |


## Best Practices

1. **Use Structured Logging**
   ```python
   # Good
   logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
   
   # Avoid
   logger.info(f"User 123 logged in from 192.168.1.1")
   ```

2. **Include Context**
   - Always include request IDs for traceability
   - Add relevant metadata to log entries

3. **Log Rotation**
   - Logs are automatically rotated at 10MB
   - Keep logs for 30 days by default

## Integration

### Python Example
```python
import logging
from pathlib import Path

# Get logger for current module
logger = logging.getLogger(__name__)


# Configure handler
log_file = Path('.windsurf/logs/my_service.log')
log_file.parent.mkdir(parents=True, exist_ok=True)

handler = logging.FileHandler(log_file)
formatter = logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] [%(request_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,%f'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Usage
logger.info("Service started", extra={"request_id": "req-123"})
```

## Monitoring

### Local Development
```powershell
# Windows PowerShell
Get-Content -Path ".windsurf\logs\*.log" -Wait

# Linux/macOS
tail -f .windsurf/logs/*.log
```

### Centralized Logging (Multi-Developer)
In a multi-developer environment, logs are automatically forwarded to the centralogging server. The central server aggregates logs from all developers and services.

#### Centralog Server Configuration
1. **Log Collection**
   - Filebeat for log shipping
   - Syslog forwarding for network devices

2. **Log Storage**
   - Centralized in `/var/log/windsurf/` on the server
   - Rotatedaily, compressed after 7 days
   - Retained for 90 days

3. **Access Control**
   - Logs are accessible via Tailscale VPN
   - Role-based access control (RBAC) for log viewing

#### Developer Workstation Setup
```powershell
# Configure log forwarding to central server
$env:WINDSURF_LOG_SERVER="central.windsurf.internal:514"

# View remote logs (requires authentication)
Invoke-RestMethod -Uri "https://central.windsurf.internal/api/logs" -Headers @{"Authorization" = "Bearer $env:WINDSURF_API_KEY"}

## Security

### Log Security
- **Redaction**: Sensitive data (API keys, passwords) is automatically redacted
- **Permissions**: Log files are only accessible to authorized users
- **Retention**: Logs are automatically purged after the retention period

### Centralized Security
1. **TLS Encryption**: Allog traffic is encrypted in transit
2. **Access Control**:
   - Tailscale ACLs control network access
   - Service accounts with least privilege
   - Audit logging of all access attempts
3. **Compliance**:
   - Logs include user attribution
   - Immutable auditrail
   - Regular security reviews

## Troubleshooting

### Local Issues
**Issue**: Logs not appearing
- Verify write permissions on `.windsurf/logs/`
- Check disk space
- Verify service has proper configuration

### Centralized Logging Issues
**Issue**: Logs not reaching central server
```powershell
# Check log forwarding service status
Get-Service windsurf-log-forwarder

# View forwarding errors
Get-Content "$env:WINDSURF_HOME\logs\log_forwarder.log" -Tail 50
```

**Issue**: Permission denied when accessing logs
- Verify Tailscale connection: `tailscale status`
- Check API key permissions
- Contact your Windsurf administrator

## SIEM Integration

Windsurf supports integration with common SIEM solutions:

### Splunk
```ini
# inputs.conf
[monitor:///var/log/windsurf/*.log]
sourcetype = windsurf
index = windsurf_logs
```

### ELK Stack
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/windsurf/*.log
  fields:
    type: windsurf
    environment: production
```

### SIEM Alerting Example
```yaml
# Example alert for failed login attempts
- alert: FailedLoginAttempts
  expr: rate(auth_failed_total[5m]) > 5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High number ofailed login attempts"
    description: "{{ $value }} failed login attempts in last 5 minutes"

---
*Last Updated: 2025-06-23*
