# 🔐 VeoGen Authentication Troubleshooting Guide

## 🚨 Current Issue: Tailscale Hostname Login Failure

### 📋 Problem Summary
- **Working**: `http://127.0.0.1:4710/` ✅ PC local access successful
- **Failing**: `http://goliath:4710/` ❌ Login screen appears but authentication fails

### 🔍 Issue Analysis

#### Frontend Access
- ✅ **Frontend loads**: Tailscale hostname resolves and serves the React frontend
- ✅ **Login form appears**: No DNS or routing issues
- ❌ **Authentication fails**: Backend API calls not working properly

#### Backend API Communication
When accessing via `http://goliath:4710/`, the frontend likely makes API calls to:
- ❌ `http://localhost:4700/api/v1/enhanced-auth/login` (wrong - localhost from frontend perspective)
- ✅ Should be: `http://goliath:4700/api/v1/enhanced-auth/login` (correct Tailscale hostname)

### 🔧 Root Cause
The React frontend uses `AuthContext.js` which determines API base URL:

```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Use relative URLs in production (proxy handles it)
  : (process.env.REACT_APP_API_URL || 'http://localhost:4700');
```

**Problem**: When accessing via `http://goliath:4710/`, the frontend still tries to call `http://localhost:4700` for API requests, but `localhost` from the perspective of the browser is the client device, not the server.

## 🛠️ Applied Fixes

### Fix #1: CORS Configuration Update ✅
Updated `backend/app/config.py` to allow Tailscale access:

```python
ALLOWED_ORIGINS: List[str] = [
    # ... existing origins ...
    # Tailscale network access
    "http://goliath:4710",  # Tailscale hostname frontend
    "http://100.118.171.110:4710",  # Tailscale IP frontend  
    "http://goliath:4700",  # Tailscale hostname backend API
    "http://100.118.171.110:4700",  # Tailscale IP backend API
    "*",  # Allow all origins for mobile access (temporary)
]
```

### Fix #2: Frontend API URL Resolution 🔧
**Status**: NEEDS IMPLEMENTATION

The frontend needs to detect when accessed via Tailscale hostname and adjust API base URL accordingly.

**Required Change**: Update `AuthContext.js` to handle hostname-based access:

```javascript
// Current logic
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Use relative URLs in production (proxy handles it)
  : (process.env.REACT_APP_API_URL || 'http://localhost:4700');

// Required logic
const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'production') {
    return ''; // Use relative URLs in production (proxy handles it)
  }
  
  // Check if accessing via Tailscale hostname
  const hostname = window.location.hostname;
  if (hostname === 'goliath') {
    return 'http://goliath:4700';
  }
  if (hostname === '100.118.171.110') {
    return 'http://100.118.171.110:4700';
  }
  
  // Default to localhost for local development
  return process.env.REACT_APP_API_URL || 'http://localhost:4700';
};

const API_BASE_URL = getApiBaseUrl();
```

## 🧪 Testing Protocol

### Test Sequence After Fix
1. **Restart Backend**: Apply CORS configuration changes
2. **Test Local Access**: Verify `http://127.0.0.1:4710/` still works
3. **Test Tailscale Hostname**: Try `http://goliath:4710/` login
4. **Test Tailscale IP**: Try `http://100.118.171.110:4710/` login
5. **Test iOS Devices**: Access via Tailscale from iPhone/iPad

### Expected Results After Complete Fix
- ✅ `http://127.0.0.1:4710/` → Works (existing)
- ✅ `http://goliath:4710/` → Works (fixed)
- ✅ `http://100.118.171.110:4710/` → Works (should work)
- ✅ iOS via Tailscale → Works (should work)

## 📊 Network Request Analysis

### Working Scenario (127.0.0.1)
```
Frontend: http://127.0.0.1:4710/ 
API Calls: http://localhost:4700/api/v1/enhanced-auth/login ✅
Result: localhost resolves to same machine, authentication succeeds
```

### Broken Scenario (goliath hostname)
```
Frontend: http://goliath:4710/
API Calls: http://localhost:4700/api/v1/enhanced-auth/login ❌  
Result: localhost resolves to client device, API unreachable
```

### Fixed Scenario (after frontend update)
```
Frontend: http://goliath:4710/
API Calls: http://goliath:4700/api/v1/enhanced-auth/login ✅
Result: goliath hostname resolves consistently, authentication succeeds
```

## 🚀 Implementation Status

### ✅ Completed
- [x] CORS configuration updated for Tailscale access
- [x] Backend restart with new CORS settings
- [x] Documentation created in proper folder structure

### 🔧 Next Steps Required
1. **Update Frontend API Logic**: Implement hostname-aware API base URL detection
2. **Restart Frontend**: Apply frontend changes
3. **Test All Access Methods**: Verify complete fix
4. **Update Documentation**: Record final working configuration

---
**Issue Priority**: HIGH - Blocks mobile/remote access to VeoGen
**Estimated Fix Time**: 15 minutes (frontend update + restart)
**Last Updated**: July 9, 2025