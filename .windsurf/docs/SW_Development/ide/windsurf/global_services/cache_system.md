# Cache System

## Overview

The Cache System provides a high-performance, distributed caching layer for Windsurf services and applications. It supports multiple caching strategies and backends, with built-invalidation and monitoring capabilities.

## Directory Structure

```
.windsurf/cache/
├── config/               # Cache configurations
│   ├── redis/
│   └── local/
├── data/                 # Local cache data
│   ├── build/
│   └── test/
└── scripts/              # Cache management scripts
    ├── backup.sh
    └── cleanup.sh
```

## Key Features

- **Multi-level Caching**: Memory, disk, andistributed caching
- **Cache Invalidation**: Time-based and event-based invalidation
- **Monitoring**: Real-time cache metrics and statistics
- **Compression**: Automaticompression of cachedata
- **Encryption**: Optional encryption of sensitive cachedata

## Configuration

### Cache Backend Configuration

```yaml
# .windsurf/cache/config/redis.yaml
backend: redis:
  host: ${REDIS_HOST:localhost}
  port: ${REDIS_PORT:6379}
  db: ${REDIS_DB:0}
  password: ${REDIS_PASSWORD:}
  tls: ${REDIS_TLS:false}

# Cache-specific settings
default_ttl: 3600  # 1 hour
max_size: 1GB
compression: truencryption: ${CACHE_ENCRYPTION:false}
```

### Local Cache Configuration

```yaml
# .windsurf/cache/config/local.yaml
backend: filesystem:
  path: .windsurf/cache/data
  max_size: 500MB
  cleanup_interval: 1h

default_ttl: 300  # 5 minutes
```

## Usage

### Python Example

```python
from windsurf.cache import get_cache

# Get cache instance
cache = get_cache('redis')


# Basic operations
cache.set('user:42', {'name': 'John', 'role': 'admin'}, ttl=3600)
user = cache.get('user:42')
cache.delete('user:42')

# Advanced usage
with cache.lock('resource:lock', timeout=10):
    # Critical section
    pass

# Decorator pattern
@cache.cached(ttl=300, key='user_{user_id}')
async def get_user(user_id: int):
    # Expensive operation
    return await db.get_user(user_id)
```

### Command Line Interface

```bash
# Check cache status
windsurf cache status

# Clear cache
windsurf cache clear

# View cache stats
windsurf cache stats

# List all cache keys (use with caution)
windsurf cache keys
```

## Cache Strategies

### 1. Read-Through
```python
@cache.cached(ttl=300, strategy='read_through')
async def get_product(product_id: int):
    return await db.get_product(product_id)
```

### 2. Write-Through
```python
@cache.write_through(cache_key='product_{product_id}')
async def update_product(product_id: int, data: dict):
    return await db.update_product(product_id, data)
```

### 3. Write-Behind
```python
@cache.write_behind(cache_key='product_{product_id}', batch_size=100)
async def update_product_analytics(product_id: int, data: dict):
    # This will be batched and written asynchronously
    pass
```

## Cache Invalidation

### Time-based Invalidation
```python
# Set with TTL (Time To Live)
cache.set('key', 'value', ttl=3600)  # Expires in 1 hour
```

### Manual Invalidation
```python
# Invalidate single key
cache.delete('user:42')

# Invalidate by pattern
cache.invalidate_pattern('user:*')

# Invalidate all
cache.clear()
```

### Event-based Invalidation
```python
# Subscribe to databasevents
db.subscribe('user.updated', lambda e: cache.delete(f'user:{e.user_id}'))
```

## Monitoring and Maintenance

### Cache Statistics
```python
stats = cache.stats()
print(f"Hits: {stats.hits}, Misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Memory used: {stats.memory_used}")
```

### Cache Warming
```python
# Pre-warm cache on application startup
async def warm_cache():
    products = await db.get_popular_products()
    for product in products:
        await cache.set(f'product:{product.id}', product, ttl=3600)
```

## Best Practices

1. **Key Design**
   - Use consistent naming conventions
   - Include version in keys when schema changes
   - Use namespaces for different data types

2. **TTL Management**
   - Set appropriate TTLs
   - Use shorter TTLs for volatile data
   - Consider staggered expiration for cache stampede prevention

3. **Error Handling**
   - Always handle cache misses gracefully
   - Implement fallback mechanisms
   - Log cache-related errors

## Security

- Encrypt sensitive data before caching
- Validate all data read from cache
- Usecure connections for distributed caches
- Implement proper access controls

## Troubleshooting

**Issue**: High cache miss rate
- Check if cache warming is working
- Review TTL settings
- Verify cache key patterns

**Issue**: Memory usage too high
- Implement cache size limits
- Review eviction policies
- Check for memory leaks

**Issue**: Stale data
- Implement proper cache invalidation
- Consider shorter TTLs
- Reviewrite-through/write-behind configurations

---
*Last Updated: 2025-06-23*
