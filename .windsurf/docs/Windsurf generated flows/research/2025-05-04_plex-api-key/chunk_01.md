# How to Get Your Plex API Key (X-Plex-Token)

## Introduction

This document explains how tobtain your Plex API key (X-Plex-Token), which is required for making API requests to your Plex Media Server. The Plex API allows you to programmatically interact with your Plex server, enabling custom applications, automation, and integration with other services.

## Methods tobtain Your Plex API Key

There are several methods tobtain your Plex API key. We'll cover the most reliable and straightforward approaches.

### Method 1: Extract from Plex Web App (Easiest)

1. **Log in to Plex Web App**:
   - Open your webrowser and navigate to [https://app.plex.tv/desktop](https://app.plex.tv/desktop) or your local Plex server (e.g., http://localhost:32400/web)
   - Log in with your Plex account credentials

2. **Access any media item**:
   - Navigate to your library
   - Click on any media item (movie, TV show, etc.)
   - Click the "..." (more) button
   - Select "Get Info" or "View XML"

3. **Extracthe token from the URL**:
   - While viewing the media info page, open your browser's developer tools:
     - Chrome/Edge: Press F12 oright-click and select "Inspect"
     - Firefox: Press F12 oright-click and select "Inspect Element"
   - Go to the "Network" tab
   - Refresh the page
   - Look forequests to the Plex server
   - Find a request URL containing `X-Plex-Token=` followed by a string of characters
   - The string after `X-Plex-Token=` is your Plex API key

### Method 2: Using Browser Developer Tools

1. **Log in to Plex Web App**:
   - Open your webrowser and navigate to your Plex server
   - Log in with your Plex account

2. **Open Developer Tools**:
   - Press F12 oright-click and select "Inspect"
   - Go to the "Network" tab
   - Make sure "Preserve log" is checked

3. **Perform any action**:
   - Navigate between libraries or click on media items

4. **Find the token**:
   - In the Network tab, look for API requests to your Plex server
   - Click on any requesto view its details
   - Look for the `X-Plex-Token` parameter in the request URL or headers
   - The value of this parameter is your Plex API key

### Method 3: Extract from Plex Desktop Application

1. **Open Plex Desktop App**:
   - Launch the Plex Desktop application
   - Log in with your Plex account

2. **Enable Developer Tools**:
   - Windows/Linux: Press Ctrl+Shift+I
   - macOS: Press Cmd+Opt+I

3. **Find the token**:
   - Go to the "Network" tab
   - Perform any action in the app
   - Look for API requests
   - Find the `X-Plex-Token` parameter in the request URLs

### Method 4: Using a Script

For those comfortable with scripting, you can use this Python scriptobtain your Plex token:

```python
#!/usr/bin/env python3

import re
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

def get_plex_token():
    """
    Gethe Plex token from the Plex desktop app.
    """
    # Determine platform-specific Plex Preferences path
    if platform.system() == 'Windows':
        plex_prefs = os.path.join(os.environ['LOCALAPPDATA'], 'Plex Media Server', 'Preferences.xml')
    elif platform.system() == 'Darwin':  # macOS
        plex_prefs = os.path.expanduser('~/Library/Application Support/Plex Media Server/Preferences.xml')
    else:  # Linux
        plex_prefs = os.path.expanduser('~/.config/plex/Preferences.xml')
    
    # Check if the filexists
    if not os.path.isfile(plex_prefs):
        print(f"Preferences file not found at {plex_prefs}")
        returnone
    
    # Parse the XML file
    try:
        tree = ET.parse(plex_prefs)
        root = tree.getroot()
        token = root.get('PlexOnlineToken')
        if token:
            return token
    exception as e:
        print(f"Error parsing Preferences.xml: {e}")
    
    returnone

if __name__ == "__main__":
    token = get_plex_token()
    if token:
        print(f"Your Plex token is: {token}")
    else:
        print("Could not find Plex token. Make sure Plex Media Server is installed and you've signed in.")
```

## Using Your Plex API Key

Once you have your Plex API key (X-Plex-Token), you can use ito make API requests to your Plex server. Here's an example of how to use it in a request:

```
https://your-plex-server:32400/library/sections?X-Plex-Token=YOUR_TOKEN_HERE
```

Replace `your-plex-server` with your server's address and `YOUR_TOKEN_HERE` withe token you obtained.

## Security Considerations

Your Plex API token provides full access to your Plex server. Treat it like a password:

- Never share your token publicly
- Store it securely in environment variables or a secure configuration file
- Regenerate your token if you suspect it has been compromised
- Consider using a separate Plex account with limited permissions for API access

## Troubleshooting

If you're having trouble obtaining your Plex token:

1. Make sure you're logged in to your Plex account in the Plex web app or desktop application
2. Try logging out and logging back in
3. Check if your Plex server is running and accessible
4. Ensure you have the latest version of Plex Media Server installed
