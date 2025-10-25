# CalibreMCP Troubleshooting Guide

## Common Issues and Solutions

### Connection Problems

#### "Library not found" Error
**Problem**: CalibreMCP cannot find your Calibre library
**Solutions**:
- Verify the library path is correct in settings
- Ensure metadata.db exists in the library directory
- Check that the path uses forward slashes (/) or double backslashes (\\)
- Try using an absolute path instead of relative

#### "Permission denied" Error
**Problem**: Cannot access library files
**Solutions**:
- Check file permissions on the library directory
- Run Claude Desktop as administrator if needed
- Ensure the library directory is not locked by Calibre

#### "Connection timeout" Error
**Problem**: Operations take too long or fail
**Solutions**:
- Increase the timeout setting in configuration
- Check if Calibre is running and responsive
- Verify network connectivity for content server
- Try reducing the default limit for large libraries

### Performance Issues

#### Slow Response Times
**Problem**: Operations are slow, especially with large libraries
**Solutions**:
- Use filtering options to narrow down searches
- Increase timeout settings
- Consider using specific library selection
- Enable caching if available

#### Memory Issues
**Problem**: High memory usage with large libraries
**Solutions**:
- Reduce default limit for list operations
- Use pagination for large result sets
- Close other applications to free memory
- Consider splitting large libraries

### Data Issues

#### Missing Books
**Problem**: Some books don't appear in results
**Solutions**:
- Check if books are in a different library
- Verify book metadata is complete
- Use cross-library search
- Check for database corruption

#### Incorrect Metadata
**Problem**: Book information is wrong or incomplete
**Solutions**:
- Use metadata update tools
- Check original book files
- Verify Calibre database integrity
- Use bulk metadata operations

### Tool-Specific Issues

#### Search Not Working
**Problem**: Search operations return no results
**Solutions**:
- Check search terms and filters
- Try different search criteria
- Verify books exist in the library
- Use basic list operations first

#### Download Failures
**Problem**: Cannot download books
**Solutions**:
- Check file permissions
- Verify book files exist
- Ensure sufficient disk space
- Check network connectivity

#### Format Conversion Issues
**Problem**: Book format conversion fails
**Solutions**:
- Verify source format is supported
- Check Calibre conversion tools are available
- Ensure sufficient disk space
- Try different output formats

## Diagnostic Tools

### Test Connection
Use the `test_calibre_connection` tool to verify basic connectivity:
```
"Test my Calibre connection and show me the results"
```

### Library Statistics
Use the `get_library_stats` tool to check library health:
```
"Show me statistics for my Calibre library"
```

### Library Health Analysis
Use the `analyze_library_health` tool for comprehensive diagnostics:
```
"Analyze my library health and suggest improvements"
```

## Getting Help

### Log Files
Check Claude Desktop logs for detailed error information:
- Look for CalibreMCP-related entries
- Check for connection errors
- Verify configuration settings

### Support Resources
- Check the CalibreMCP documentation
- Review the quick start guide
- Look for similar issues in the community
- Contact support with specific error messages

### Reporting Issues
When reporting issues, include:
- Error messages (exact text)
- Configuration settings (without sensitive data)
- Library size and structure
- Steps to reproduce the problem
- Claude Desktop version and platform
