# Nginx Guide for Documentation Hosting

## Table of Contents
- [Introduction](#introduction)
- [When to Use Nginx](#when-to-use-nginx)
- [Basic Setup](#basic-setup)
- [Advanced Configuration](#advanced-configuration)
- [Performance Tuning](#performance-tuning)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Alternatives](#alternatives)

## Introductionginx (pronounced "engine-x") is a high-performance web server, reverse proxy, and load balancer. This guide covers usinginx with our Docsify documentation system.

## When to Use Nginx

### Use Nginx When:
- Serving documentation to the public internet
- Need SSL/TLS termination
- Require advanced caching
- Need load balancing
- Wanto serve multiple applications
- Need rate limiting or access control

### Tailscale-Only Alternative
For internal documentation accessible only via Tailscale, you can use the simpler [Tailscale Docsify setup](../scripts/start-docsify-tailscale.ps1) without Nginx.

## Basic Setup

### Installation
```powershell
# Windows (using Chocolatey)
choco install nginx

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install nginx

# Linux (RHEL/CentOS)
sudo yum install epel-release
sudo yum install nginx
```

### Basiconfiguration
```nginx
# /etc/nginx/conf.d/docs.conf
server {
    listen 80;
    server_name docs.yourdomain.com;
    
    location / {
        root /path/to/your/docs;
        index.html;
        
        # Enable gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascriptext/xml application/xml application/xml+rss text/javascript;
        
        # Handle HTML5 History Mode
        try_files $uri $uri/ /index.html;
    }
}
```

## Advanced Configuration

### SSL with Let's Encrypt
```nginx
server {
    listen 80;
    server_name docs.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name docs.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/docs.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    
    # HSTS (uncomment after testing)
    # add_header Strict-Transport-Security "max-age=63072000" always;
    
    location / {
        root /path/to/your/docs;
        index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

### Caching Headers
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    log_not_found off;
}
```

## Performance Tuning

### Worker Processes
```nginx
# Seto number of CPU cores
worker_processes auto;

events {
    # Max connections per worker_connections 1024;
    
    # Efficient connection processing
    usepoll; # Linux only
    multi_accept on;
}

http {
    # Buffer size for headers
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;
    
    # File handling
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # Gzip settings
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_vary on;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifestext/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vttext/x-componentext/x-cross-domain-policy;
}
```

## Security

### Basic Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_headereferrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Permissions-Policy "geolocation=(), midi=(), sync-xhr=(), microphone=(), camera=(), magnetometer=(), gyroscope=(), fullscreen=(self)" always;
```

### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

server {
    # ... other server config ...
    
    location / {
        limit_req zone=one burst=20 nodelay;
        # ... other location config ...
    }
}
```

## Troubleshooting

### Common Issues

#### 404 Errors
- Check file permissions
- Verify root directory path
- Ensure index.html exists

#### Permission Denied
```bash
# Fix Nginx user permissionsudo chown -R nginx:nginx /path/to/your/docsudo chmod -R 755 /path/to/your/docs
```

#### Check Configuration
```bash
# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Alternatives to Nginx

### For Simple Setups
- [Caddy](https://caddyserver.com/) - Automatic HTTPS by default
- [Traefik](https://traefik.io/) - Cloud-nativedge router
- [Docsify's built-in server](https://docsify.js.org/#/quickstart) - For development only

### For Advanced Setups
- [Apache](https://httpd.apache.org/) - Traditional web server
- [HAProxy](http://www.haproxy.org/) - High availability load balancer
- [Cloudflare](https://www.cloudflare.com/) - CDN with security features

## Next Steps
1. [Secure your Nginx server](https://geekflare.com/nginx-webserver-security-hardening-guide/)
2. Set up monitoring with [Prometheus and Grafana](https://grafana.com/)
3. Configure automated backups
4. Implement CI/CD for documentation updates
