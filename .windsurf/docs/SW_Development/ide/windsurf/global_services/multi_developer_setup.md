# Multi-Developer Setup with Centralized Services

## Table of Contents
1. [Overview](#overview)
2. [Centralized Services Architecture](#centralized-services-architecture)
3. [Network Setup with Tailscale](#network-setup-with-tailscale)
4. [Security Implementation](#security-implementation)
5. [Developer Workstation Configuration](#developer-workstation-configuration)
6. [Monitoring and SIEM Integration](#monitoring-and-siem-integration)
7. [Troubleshooting](#troubleshooting)

## Overview

This document outlines how to set up and use Windsurf's global services in a multi-developer environment across different locations. Thisetup ensures consistent development experience while maintaining security and access control.

## Centralized Services Architecture

### Serverequirements
- **Hardware**: Minimum 4 CPU cores, 8GB RAM, 100GB storage
- **Operating System**: Windowserver 2022 or Ubuntu 22.04 LTS
- **Network**: Static IP or dynamic DNSetup

### Service Components
1. **Core Services**
   - Centralized logging
   - Configuration store
   - Rulebookservice
   - Template library
   - Shared libraries
   - Documentation hub

2. **Network Services**
   - Tailscale VPN
   - Nginx reverse proxy
   - Let's Encrypt SSL certificates

## Network Setup with Tailscale

### 1. Install Tailscale
```powershell
# On Windows
winget install Tailscale.Tailscale

# On Linux
curl -fsSL https://tailscale.com/install.sh | sh
```

### 2. Initial Setup
1. Create a Tailscale account at https://login.tailscale.com/start
2. Authenticateach machine:
   ```powershell
   tailscale up
   ```
3. Note the Tailscale IP assigned to your central server

### 3. Network Configuration
1. **Subnet Routing** (Optional):
   ```powershell
   # On the central server
   tailscale up --advertise-routes=192.168.1.0/24 --accept-routes
   ```

2. **DNS Configuration**:
   - Enable MagicDNS in Tailscale admin console
   - Set up custom DNS names (e.g., `central.windsurf.internal`)

## Security Implementation

### 1. Access Control
- **Tailscale ACLs** (`/etc/tailscale/acls.json`):
  ```json
  {
    "acls": [
      {
        "action": "accept",
        "src": ["autogroup:member"],
        "dst": ["central-server:443"]
      }
    ]
  }
  ```

### 2. Service Authentication
1. **API Keys**:
   ```powershell
   # Generate API key
   $apiKey = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
   $env:WINDSURF_API_KEY = $apiKey
   ```

2. **Environment Configuration** (`.windsurf/config`):
   ```ini
   [central]
   url = https://central.windsurf.internal
   api_key = ${env:WINDSURF_API_KEY}
   ```

## Developer Workstation Configuration

### 1. Prerequisites
- Git
- PowerShell 7+
- Node.js LTS (if using web interfaces)

### 2. Setup Script
```powershell
# Install required modules
Install-Module -Name PowerShellGet -Force -AllowClobber
Install-Module -Name PSScriptAnalyzer -Force

# Clone repository
git clone https://your-repo-url/windsurf-project.git
cd windsurf-project

# Set environment variables
$env:WINDSURF_HOME = "$pwd\.windsurf"
$env:PATH += ";$pwd\.windsurf\bin"

# Verify connectivity
Test-NetConnection central.windsurf.internal -Port 443
```

## Monitoring and SIEM Integration

### 1. Centralized Logging
- All services write to `.windsurf/logs/`
- Logs are forwarded to the central SIEM

### 2. SIEM Components
1. **Log Collection**:
   - Filebeat for log shipping
   - Syslog forwarding for network devices

2. **Alerting Rules** (Example for Grafana):
   ```yaml
   - alert: HighErrorRatexpr: rate(log_entries{level="error"}[5m]) > 10
     for: 10m
     labels:
       severity: critical
     annotations:
       summary: High errorate detected
   ```

## Troubleshooting

### Common Issues

**1. Connection Timeouts**
```powershell
# Check Tailscale status
tailscale status

# Test basiconnectivity
Test-NetConnection central.windsurf.internal -Port 443

# Check service status
Get-Service windsurf-* | Select-Object Name, Status
```

**2. Permission Denied**
- Verify Tailscale ACLs
- Check API key permissions
- Ensure user is in the correct groups

**3. Service Unavailable**
```powershell
# Check service logs
Get-Content "$env:WINDSURF_HOME\logs\windsurf_services.log" -Tail 50

# Verify service is runninget-Process -Name "windsurf-*"
```

## Maintenance

### Regular Tasks
1. **Backup**:
   ```powershell
   # Daily backup script
   Compress-Archive -Path "$env:WINDSURF_HOME" -DestinationPath "backups\windsurf-$(Get-Date -Format 'yyyyMMdd').zip"
   ```

2. **Updates**:
   - Weekly Tailscale updates
   - Monthly service updates

---
*Last Updated: 2025-06-23*
