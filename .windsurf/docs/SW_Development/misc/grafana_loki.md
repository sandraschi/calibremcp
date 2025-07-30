# Grafana & Loki: Complete Guide

## Table of Contents
- [Authentication & Security](#authentication--security)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Log Queries](#log-queries)
- [Dashboards](#dashboards)
- [Alerting](#alerting)
- [Backup & Restore](#backup--restore)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)
- [API Reference](#api-reference)

## Authentication & Security

### Default Credentials
- **URL**: `http://<server-ip>:3140`
- **Username**: `admin`
- **Password**: `windsurf123` (change this in production)

### Changing Admin Password

1. **Web UI Method**:
   - Log in as admin
   - Click on the user icon (bottom left) → Preferences → Change Password

2. **Environment Variable**:
   Update `docker-compose.logs.yml`:
   ```yaml
   environment:
     - GF_SECURITY_ADMIN_PASSWORD=your_new_secure_password
   ```
   Then restarthe service:
   ```powershell
   docker-compose -f docker-compose.logs.yml up -d
   ```

### Securing Access
- **HTTPS**: Configureverse proxy with TLS
- **IP Whitelisting**: Use Tailscale ACLs
- **Authentication**: Enable OAuth2 or LDAP in Grafana

## Architecture

### Components

1. **Grafana**
   - Web UI for visualization
   - Runs on port 3140
   - Stores dashboards and user preferences

2. **Loki**
   - Log aggregation system
   - Runs on port 3100
   - Indexes log metadata, not content

### Data Flow
```
Application Logs → Loki (Indexing) → Grafana (Visualization)
```

## Configuration

### Grafana Configuration
Location: `grafana/provisioning/`

1. **Data Sources** (`datasources/loki.yml`):
   ```yaml
   apiVersion: 1
   datasources:
     - name: Loki
       type: loki
       access: proxy
       url: http://loki:3100
       version: 1
       editable: true
   ```

2. **Dashboards** (Optional):
   - Store in `grafana/provisioning/dashboards/`
   - Reference in `dashboards.yml`

### Loki Configuration
Default config in `docker-compose.logs.yml`:
```yaml
services:
  loki:
    command: -config.file=/etc/loki/local-config.yaml
```

## Log Queries

### Basic Queries
```
# Show allogs
{filename="/logs/*.log"}

# Filter by log level
{filename="/logs/*.log"} |~ "(?i)error"

# Time range
{filename="/logs/*.log"} |~ "error" |~ "exception"
```

### LogQL Reference

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equality matcher | `{app="myapp"}` |
| `!=` | Not equal | `{app!="debug"}` |
| `=~` | Regex match | `{app=~"prod.*"}` |
| `!~` | Negative regex | `{app!~"test.*"}` |
| `|~` | Line contains | `|~ "error"` |
| `|~` | Regex filter | `|~ "(?i)critical"` |
| `| json` | Parse JSON logs | `| json` |

## Dashboards

### Importing Dashboards
1. Click '+' → Import
2. Enter dashboard ID or paste JSON
3. Select Loki as data source

### Recommendedashboards
1. **Loki Logs Overview**
   - ID: 13639
   - Shows log volume and patterns

2. **Kubernetes Logs**
   - ID: 10601
   - If using Kubernetes

## Alerting

### Setting Up Alerts
1. Go to Alert → Alert rules
2. Create new rule
3. Define query and conditions

### Example Alert Rule
```yaml
# Save as alert-rules.yml in grafana/provisioning/alerting/
groups:
  - name: CriticalErrors
    rules:
      - alert: HighErrorRatexpr: 'sum(rate({filename="/logs/*.log"} |~ "ERROR" [5m])) by (level) > 10'
        for: 10m
        labels:
          severity: 'critical'
        annotations:
          summary: 'High errorate detected'
```

## Backup & Restore

### Backing Up
```powershell
# Create backup directory
$backupDir = "grafana_backup_$(Get-Date -Format 'yyyyMMdd')
mkdir $backupDir

# Backup Grafana data
docker cp grafana:/var/lib/grafana/grafana.db "$backupDir/grafana.db"

# Backup Loki data (if using persistent storage)
docker cp loki:/data "$backupDir/loki_data"

# Backup configurations
Copy-Item -Path "grafana/provisioning" -Destination "$backupDir/" -Recurse
```

### Restoring
```powershell
# Stop services
docker-compose -f docker-compose.logs.yml down

# Restore Grafana
docker cp "$backupDir/grafana.db" grafana:/var/lib/grafana/

# Restore Loki (if needed)
docker cp "$backupDir/loki_data/" loki:/data

# Start services
docker-compose -f docker-compose.logs.yml up -d
```

## Troubleshooting

### Common Issues

#### 1. Can't Access Grafana
```powershell
# Check if containers are running
docker ps

# Check logs
docker-compose -f docker-compose.logs.ymlogs grafana

# Check port usage
netstat -ano | findstr :3140
```

#### 2. No Logs Appearing
```powershell
# Check Loki logs
docker-compose -f docker-compose.logs.ymlogs loki

# Verify log directory permissions
docker exec -it loki ls -la /logs

# Check Loki health
curl http://localhost:3100/ready
```

#### 3. High Resource Usage
```powershell
# Check container stats
docker stats

# Increase resources in docker-compose.logs.yml
services:
  loki:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Performance Tuning

### Loki Configuration
Edit `loki-config.yaml`:
```yaml
auth_enabled: falserver:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s
  max_transfer_retries: 0

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_ttl: 24h
    shared_store: filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 32
  ingestion_burst_size_mb: 64

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 744h
```

### Grafana Performance
1. **Increase Cache**:
   ```yaml
   environment:
     - GF_DATASOURCE_CACHE_MAX_MEMORY_MB=1000
   ```

2. **Enable Gzip**:
   ```yaml
   environment:
     - GF_SERVER_ENABLE_GZIP=true
   ```

## API Reference

### GrafanaPI
```
GET    /api/health
GET    /api/dashboards/uid/:uid
POST   /api/dashboards/db
DELETE /api/dashboards/uid/:uid
```

### Loki API
```
GET    /loki/api/v1/query
GET    /loki/api/v1/query_rangeT    /loki/api/v1/labels
GET    /loki/api/v1/label/{name}/values
POST   /loki/api/v1/push
```

## Security Best Practices

1. **Change Default Credentials**
   - Change admin password immediately
   - Create separate users with minimal required permissions

2. **Network Security**
   - Use Tailscale for secure access
   - Configure firewall rules
   - Enable HTTPS

3. **Audit Logs**
   - Monitor Grafanaudit logs
   - Set up alerts for suspicious activities

4. **Regular Updates**
   - Keep Grafanand Loki updated
   - Monitor security advisories

## Monitoring

### Built-in Dashboards
1. **Grafana Metrics**
   - Go to Home → Dashboards → Manage
   - Import dashboard ID: 10856

2. **Loki Metrics**
   - Import dashboard ID: 13639

### External Monitoring
- **Prometheus**: Scrape Grafanand Loki metrics
- **Alertmanager**: Route alerts to email/Slack

## Scaling

### Vertical Scaling
```yaml
services:
  loki:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### Horizontal Scaling
1. Run multiple Loki read/write nodes
2. Use shared object storage (S3, GCS)
3. Configure Lokin microservices mode

## Backup Strategy

### Daily Backups
```powershell
# Create backup script: backup-grafana.ps1
$backupDir = "D:\backups\grafana-$(Get-Date -Format 'yyyyMMdd')
New-Item -ItemType Directory -Path $backupDir -Force

docker cp grafana:/var/lib/grafana/grafana.db "$backupDir\grafana.db"

# Keep backups for 30 days
Get-ChildItem "D:\backups" -Directory | 
  Where-Object { $_.Name -match 'grafana-\d{8}' -and $_.CreationTime -lt (Get-Date).AddDays(-30) } | 
  Remove-Item -Recurse -Force
```

### Scheduled Task
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\scripts\backup-grafana.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Grafana Backup" -Description "Daily Grafana backup"
```

## Common Tasks

### Reset Admin Password
```powershell
docker exec -it grafana-cli admin reset-admin-password newpassword
```

### View Loki Logs
```powershell
docker-compose -f docker-compose.logs.ymlogs -f loki
```

### Access Loki Shell
```powershell
docker exec -it loki /bin/sh
```

## Troubleshootinguide

### Log Collection Issues
1. **No logs appearing**
   - Check if log files exist in the mounted volume
   - Verify Loki can access the log directory
   - Check Loki logs for errors

2. **High latency**
   - Increase resources
   - Adjust chunk settings
   - Check network latency

3. **Storage issues**
   - Monitor disk space
   - Adjust retention policies
   - Clean up old chunks

## Getting Help

### Official Documentation
- [Grafana Docs](https://grafana.com/docs/)
- [Loki Docs](https://grafana.com/docs/loki/latest/)

### Community Support
- [Grafana Community Forums](https://community.grafana.com/)
- [GitHub Issues](https://github.com/grafana/loki/issues)
