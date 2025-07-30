# Configuration Store

## Overview

The Configuration Store provides a secure and centralized way to manage configuration settings across all Windsurf services and repositories. It supports environment-specificonfigurations, secrets management, andynamiconfiguration updates.

## Directory Structure

```
.windsurf/config/
├── global/                 # Global configurations
│   ├── database.yml
│   ├── security.yml
│   └── services/
│       ├── api.yml
│       └── worker.yml
├── environments/           # Environment-specificonfigs
│   ├── development/
│   │   ├── database.yml
│   │   └── services/
│   ├── staging/
│   └── production/
├── secrets/               # Encrypted secrets
│   ├── api-keys.enc
│   └── certificates/
└── templates/             # Configuration templates
    └── service-config.tpl
```

## Key Features

- **Environment-aware**: Different settings per environment
- **Secrets Management**: Secure storage of sensitive data
- **Templating**: Reusable configuration templates
- **Validation**: Schema validation for configurations
- **Versioning**: Track changes to configurations

## Configuration Files

### Global Configuration
Located in `.windsurf/config/global/`, thesettings apply to all environments.

### Environment-specificonfiguration
Located in `.windsurf/config/environments/{env}/`, these override global settings.

### Secrets Management
Sensitive data istored encrypted in `.windsurf/config/secrets/`.

## Usage

### Accessing Configuration

#### Python Example
```python
from windsurf.config import Config

# Load configuration
config = Config.load('service-name', environment='production')

# Access values
db_config = config.database
api_key = config.get_secret('api_key')
```

#### Shell Example
```bash
# Get configuration value
windsurf configet database.host

# Set configuration value
windsurf config set database.host=localhost --environment=development

# Encrypt secret
windsurf secrets encrypt my-secret-value > .windsurf/config/secrets/api-key.enc
```

## Configuration Format

### YAML Example
```yaml
# .windsurf/config/global/database.yml
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: ${DB_NAME:myapp}
  user: ${DB_USER:postgres}

  # Connection pool settings
  pool:
    min: 1
    max: 10
    idle_timeout: 300

  # SSL configuration
  ssl:
    enabled: true
    ca: ${DB_CA_PATH:/path/to/ca.pem}
    verify: true
```

## Best Practices

1. **Usenvironment Variables**
   - Store sensitive data in environment variables
   - Use `${VARIABLE:default}` syntax for optional values

2. **Keep Secretsecure**
   - Never commit unencrypted secrets
   - Use `windsurf secrets` for encryption

3. **Validate Configurations**
   - Define schemas for configurations
   - Validate on application startup

## Security

- **Encryption**: All secrets arencrypted at rest
- **Access Control**: Role-based access to configurations
- **Audit Log**: All access is logged

## Integration

### Environment Setup
```bash
# Set environment variables
export WINDSURF_ENV=development
export WINDSURF_CONFIG_PATH=./.windsurf/config
```

### Docker Integration
```dockerfile
FROM python:3.9

# Install windsurf-cli
RUN pip install windsurf-cli

# Copy configuration
COPY .windsurf/config /app/.windsurf/config

# Set environment
ENV WINDSURF_ENV=production
ENV WINDSURF_CONFIG_PATH=/app/.windsurf/config

# Your application code
COPY . /app
WORKDIR /app

CMD ["your-app"]
```

## Troubleshooting

**Issue**: Configurationot loading
- Verify `WINDSURF_CONFIG_PATH` iset correctly
- Check file permissions
- Ensurenvironment is properly set

**Issue**: Secrets not decrypting
- Verify encryption key is available
- Check file permissions on secrets
- Ensure correct environment iselected

## Version Control

- Commit configuration templates
- Never commit unencrypted secrets
- Use `.gitignore` to exclude sensitive files

---
*Last Updated: 2025-06-23*
