# Immich: Self-Hosted Photo and Video Backup Solution

## Overview
Immich is a high-performance, self-hosted photo and video backup solution that provides a Google Photos-likexperience. It's designed to be fast, reliable, and privacy-focused, allowing you to maintain full control over your personal media.

## Key Features

### 1. Media Management
- **Automatic Organization**: Chronological timeline view
- **Face Recognition**: AI-powered face grouping
- **Object Detection**: Automatically tag photos by content
- **Location-Based**: View photos on a map
- **Search**: Powerful search by date, location, people, and objects

### 2. Backup & Sync
- **Mobile Apps**: Automatic backup from iOS and Android
- **Web Upload**: Drag androp from any browser
- **CLI Tool**: For advanced users and automation
- **Selective Sync**: Choose which albums to sync

### 3. Sharing
- **Albums**: Create and share photo albums
- **Public Links**: Generate shareable links
- **Collaboration**: Shared albums with multiple contributors

## Architecture

### Core Components
1. **Server**: Main application server (Node.js + NestJS)
2. **Web**: React-based web interface
3. **Mobile**: React Native apps for iOS and Android
4. **Microservices**:
   - Machine Learning (face/object recognition)
   - Reverse Proxy (Nginx)
   - Database (PostgreSQL)
   - Redis (caching)
   - Typesense (search)

### Data Flow
1. Client uploads media
2. Server processes and stores original files
3. Background jobs generate thumbnails and optimize versions
4. Machine learning services analyze content
5. Metadata is indexed for fast searching

## Installation

### Prerequisites
- Docker andocker Compose
- At least 4GB RAM (8GB+ recommended)
- 64-bit system

### Quick Start
```bash
# Create project directory
mkdir immich && cd immich

# Downloadocker-compose.yml
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml

# Create .env file
cat > .env <<EOL
# Database
DB_HOSTNAME=immich_postgres
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE_NAME=immich

# Redis_HOSTNAME=immich_redis

# Upload location (change as needed)
UPLOAD_LOCATION=/usr/src/app/upload

# JWT Secret (change this!)
JWT_SECRET=your-super-secret-jwt-token
EOL

# Start services
docker-compose up -d
```

### Advanced Installation

#### 1. Custom Volumes
```yaml
services:
  immich_server:
    volumes:
      - /path/to/upload:/usr/src/app/upload
      - /path/to/config:/config
```

#### 2. External Database
```yaml
services:
  immich_postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: immich
      POSTGRES_PASSWORD: your-db-password
      POSTGRES_DB: immich
    volumes:
      - /path/to/postgres/data:/var/lib/postgresql/data
```

## Configuration

### Environment Variables

#### Required
- `UPLOAD_LOCATION`: Where to store uploaded files
- `JWT_SECRET`: Secret for JWToken generation
- `DB_*`: Database connection details
- `REDIS_HOSTNAME`: Redis hostname

#### Optional
- `NODE_ENV`: Seto 'production' for production
- `TYPESENSE_ENABLED`: Enable/disable search (default: true)
- `MACHINE_LEARNING_ENABLED`: Enable/disable ML features
- `THUMBNAIL_WIDTH`: Width of generated thumbnails (default: 250)

### Reverse Proxy Setup

#### Nginx Example
```nginx
server {
    listen 80;
    server_name photos.example.com;
    
    location / {
        proxy_pass http://localhost:2283;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Increase client max body size for large uploads
    client_max_body_size 5000M;
}
```

## Usage

### Web Interface
1. Access at `http://localhost:2283`
2. Create admin account on first run
3. Start uploading photos and videos

### Mobile Apps
1. Download from [GitHub Releases](https://github.com/immich-app/immich-mobile/releases)
2. Connecto your server URL
3. Enable auto-backup in settings

### CLI Tool
```bash
# Install CLI
npm install -g @immich/cli

# Login
immich login --server http://your-server-address --api-keyour-api-key

# Uploadirectory
immich upload /path/to/photos

# View status
immich status
```

## Backup Strategy

### 1. Database Backups
```bash
# Create backup
docker exec immich_postgres pg_dump -U postgres immich > immich_backup_$(date +%Y%m%d).sql

# Restore
cat immich_backup.sql | docker exec -immich_postgres psql -U postgres immich
```

### 2. Media Backups
```bash
# Simple rsync example
rsync -avz /path/to/immich/upload/ user@backup-server:/backup/immich/
```

## Maintenance

### Updates
```bash
# Pullatest images
docker-compose pull

# Restart services
docker-compose up -d

# Run migrations (if needed)
docker-compose run --rm immich_server npm run migration:run
```

### Cleanup
```bash
# Remove unusedockeresources
docker system prune

# Clean up oldocker images
docker image prune -a
```

## Monitoring

### Logs
```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f immich_server
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Check API health
curl http://localhost:2283/api/server-info/statistics
```

## Security

### Authentication
- JWT-based authentication
- OAuth 2.0 support
- 2FA (Two-Factor Authentication)

### Data Protection
- Filestored with random UUIDs
- Optional client-sidencryption
- Role-based access control

## Performance Tuning

### Database Optimization
```sql
-- Run in PostgreSQL
VACUUM ANALYZE;
CREATE INDEX IF NOT EXISTS assets_created_at_idx ON assets(created_at);
```

### Memory Management
```yaml
# In docker-compose.yml
services:
  immich_server:
    environment:
      - NODE_OPTIONS=--max_old_space_size=4096
```

## Troubleshooting

### Common Issues

#### 1. Upload Failures
- Check disk space
- Verify file permissions
- Increase clientimeout settings

#### 2. Face Recognitionot Working
- Ensure MACHINE_LEARNING_ENABLED=true
- Check GPU availability for ML processing
- Verify sufficient system resources

#### 3. Slow Performance
- Add more RAM
- Enable Redis caching
- Optimize database indexes

## API Documentation

### Authentication
```httpOST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

### Upload Asset
```httpOST /asset/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

# Form data:
# file: [binary file data]
# albumId: (optional)
# isFavorite: (boolean)
```

## Community & Support

### Resources
- [GitHub Repository](https://github.com/immich-app/immich)
- [Documentation](https://immich.app/)
- [Discord Community](https://discord.gg/D8JsnBEuKb)

### Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
MIT License - See [LICENSE](https://github.com/immich-app/immich/blob/main/LICENSE) for details.
