# CalibreMCP Configuration Guide

## Configuration Options

CalibreMCP can be configured through user settings in Claude Desktop. Here are the available configuration options:

### Library Configuration

#### Calibre Library Path
- **Type**: Directory
- **Required**: Yes
- **Default**: `L:/Multimedia Files/Written Word/Calibre-Bibliothek`
- **Description**: Path to your main Calibre library directory (contains metadata.db)

#### Calibre Server URL
- **Type**: String
- **Required**: No
- **Default**: Empty
- **Description**: URL of your Calibre content server (optional, for remote access)

### Performance Settings

#### Operation Timeout
- **Type**: String
- **Default**: `30`
- **Description**: Timeout in seconds for Calibre operations

#### Default Limit
- **Type**: String
- **Default**: `100`
- **Description**: Default number of results to return in list operations

### Advanced Settings

#### Enable Debug Logging
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable detailed logging for troubleshooting

#### Cache Duration
- **Type**: String
- **Default**: `3600`
- **Description**: Cache duration in seconds for library metadata

## Configuration Examples

### Local Library Only
```json
{
  "calibre_library_path": "L:/Multimedia Files/Written Word/Calibre-Bibliothek",
  "calibre_server_url": "",
  "timeout": "30"
}
```

### With Content Server
```json
{
  "calibre_library_path": "L:/Multimedia Files/Written Word/Calibre-Bibliothek",
  "calibre_server_url": "http://localhost:8080",
  "timeout": "60"
}
```

### High-Performance Setup
```json
{
  "calibre_library_path": "L:/Multimedia Files/Written Word/Calibre-Bibliothek",
  "timeout": "120",
  "default_limit": "500",
  "cache_duration": "7200"
}
```

## Environment Variables

You can also configure CalibreMCP using environment variables:

- `CALIBRE_LIBRARY_PATH` - Path to Calibre library
- `CALIBRE_SERVER_URL` - Calibre content server URL
- `CALIBRE_USERNAME` - Username for content server
- `CALIBRE_PASSWORD` - Password for content server
- `CALIBRE_TIMEOUT` - Operation timeout
- `CALIBRE_DEFAULT_LIMIT` - Default result limit

## Best Practices

### Library Path
- Use absolute paths for reliability
- Ensure the path contains metadata.db
- Avoid paths with special characters or spaces

### Performance
- Increase timeout for large libraries (10,000+ books)
- Use appropriate limits to balance performance and completeness
- Enable caching for frequently accessed data

### Security
- Use environment variables for sensitive information
- Avoid hardcoding credentials in configuration
- Regularly update API keys and passwords
