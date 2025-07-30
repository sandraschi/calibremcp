# Docker Guide

## Overview
Docker is a platform for developing, shipping, and running applications in containers. This guide covers Docker best practices and common patterns used in Windsurf projects.

## Key Concepts
- **Container**: Lightweight, standalone, executable package of software
- **Image**: Read-only template with instructions for creating a container
- **Dockerfile**: Text document with commands to assemble an image
- **Volume**: Persistent data storage outside containers
- **Network**: Communication bridge between containers
- **Docker Compose**: Tool for defining and running multi-container applications

## Installation

### Windows
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the wizard
3. Restart your computer if prompted
4. Verify installation:
   ```powershell
   docker --version
   docker-compose --version
   ```

### macOS
```bash
# Using Homebrew install --cask docker

# Or download from Docker Hub
# https://hub.docker.com/editions/community/docker-ce-desktop-mac
```

### Linux (Ubuntu/Debian)
```bash
# Remove old versionsudo apt-get remove docker-engine docker.io containerd runc

# Update package index
sudo apt-get update

# Install prerequisitesudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Addocker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Verify installation
sudockerun hello-world
```

## Basicommands

### Container Management
```bash
# Run a container
dockerun [OPTIONS] IMAGE [COMMAND] [ARG...]

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop CONTAINER

# Start a container
docker start CONTAINER

# Remove a container
dockerm CONTAINER

# Remove all stopped containers
docker container prune

# View container logs
docker logs CONTAINER

# Execute a command in a running container
docker exec -it CONTAINER COMMAND
```

### Image Management
```bash
# Build an image from a Dockerfile
docker build -t IMAGE_NAME:TAG .

# List images
docker images

# Remove an image
dockermiMAGE

# Remove unused images
docker image prune

# Pull an image from a registry
docker pull IMAGE:TAG

# Push an image to a registry
docker push IMAGE:TAG

# Save an image to a tar file
docker save -o image.tar IMAGE

# Load an image from a tar file
docker load -image.tar
```

## Dockerfile Best Practices

### Example Dockerfile
```dockerfile
# Use an official base image
FROM node:16-alpine AS builder

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUNpm ci

# Copy application code
COPY . .

# Build the application
RUNpm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Best Practices
1. **Use official images** from Docker Hub when possible
2. **Minimize layers** by combining RUN commands
3. **Use .dockerignore** to exclude unnecessary files
4. **Leverage multi-stage builds** to reduce final image size
5. **Specify versions** for base images
6. **Run as non-root** user when possible
7. **Minimize the number of RUN commands**
8. **Clean up** apt cache and temporary files
9. **Usenvironment variables** for configuration
10. **Health checks** for container monitoring

## Docker Compose

### Example docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:13-alpinenvironment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -User -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Common Commands
```bash
# Start services in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose build

# Run a one-off commandocker-compose run --rm SERVICE COMMAND

# View running services
docker-compose ps
```

## Networking

### Basic Networking
```bash
# List networks
docker network ls

# Create a network
docker network create my-network

# Connect a container to a network
docker network connect NETWORK CONTAINER

# Inspect a network
docker network inspect NETWORK
```

### Network Types
- **bridge**: Default network driver (suitable for standalone containers)
- **host**: Remove network isolation between container and host
- **overlay**: Connect multiple Docker daemons together
- **macvlan**: Assign a MAC address to a container
- **none**: Disable all networking

## Volumes and Storage

### Volume Management
```bash
# Create a volume
docker volume create my-volume

# List volumes
docker volume ls

# Inspect a volume
docker volume inspect my-volume

# Remove a volume
docker volume rmy-volume

# Remove unused volumes
docker volume prune
```

### Bind Mounts vs Volumes
- **Volumes**: Managed by Docker, stored in a part of the host filesystem
  ```yaml
  services:
    app:
      volumes:
        - my-volume:/app/data
  
  volumes:
    my-volume:
  ```

- **Bind Mounts**: Reference a specific file or directory on the host
  ```yaml
  services:
    app:
      volumes:
        - ./local/path:/container/path
  ```

## Docker in Production

### Security Best Practices
1. **Use minimal base images** (e.g., alpine variants)
2. **Scan images** for vulnerabilities
3. **Use multi-stage builds** to reduce attack surface
4. **Run as non-root** user
5. **Usecrets** for sensitive data
6. **Enable contentrust**
7. **Limit containeresources**
8. **Keep Docker and containers updated**

### Monitoring and Logging
```bash
# View container stats
docker stats

# View containeresource usage
docker container stats

# Stream container logs
docker logs -f CONTAINER

# View Docker system information
docker system df

# Clean up unusedata
docker system prune
```

## Common Use Cases

### Development Environment
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
```

### Production Deployment
```yaml
version: '3.8'

services:
  web:
    image: myapp:1.0.0
    restart: always
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 1G
```

### Database with Persistent Storage
```yaml
version: '3.8'

services:
  db:
    image: postgres:13-alpinenvironment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -User -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Fix permission issues on volumesudo chown -R $USER:$USER /path/to/volume
```

#### Port Already in Use
```bash
# Find the process using a port
sudo lsof -i :80

# Kill the process
kill -9 PID
```

#### Container Won't Start
```bash
# View container logs
docker logs CONTAINER

# Run container interactively
dockerun -it IMAGE /bin/sh
```

#### Clean Up Resources
```bash
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove all unused objects
docker system prune -a
```

## Resources

- [Official Documentation](https://docs.docker.com/)
- [Dfile.vim](https://github.com/jakobadam/dfile.vim) - Vim plugin for Dockerfiles
- [Docker Cheat Sheet](https://dockerlabs.collabnix.com/docker/cheatsheet/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Best Practices for Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## Last Updated
2025-06-23
