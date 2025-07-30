# Plex: Ultimate Media Server Solution

## Overview
Plex is a powerful media server platform that organizes and streams your personal media collection to all your devices. It automatically fetches rich metadata, artwork, and related contento create a beautiful, Netflix-likexperience for your personal media library.

## Core Components

### 1. Plex Media Server
- **Media Organization**: Automatically organizes your media files
- **Metadata Fetching**: Retrieves movie/TV show information, artwork, and more
- **Transcoding**: On-the-fly media conversion for optimal playback
- **User Management**: Create managed users with different access levels

### 2. Plex Clients
- **Web Player**: Access your media from any browser
- **Desktop Apps**: Native apps for Windows, macOS, and Linux
- **Mobile Apps**: iOS and Android apps for on-the-go access
- **SmartV Apps**: Available on most SmartV platforms
- **Game Consoles**: Apps for PlayStation, Xbox, and Nintendo Switch

### 3. Plex Pass (Premium Features)
- **Mobile Sync**: Download media for offline viewing
- **Hardware Acceleration**: Faster transcoding with GPU support
- **Trailers & Extras**: Additional bonus content
- **Lyricsupport**: Display synchronized lyrics for music
- **Early Access**: Try new features before general release

## Installation

### Windows
```powershell
# Download and install from official website
# https://www.plex.tv/media-server-downloads/

# Or using Chocolatey (unofficial)
choco install plexmediaserver
```

### Linux
```bash
# Ubuntu/Debian
curl https://downloads.plex.tv/plex-keys/PlexSign.key | sudo apt-key add -
echo deb https://downloads.plex.tv/repo/deb public main | sudo tee /etc/apt/sources.list.d/plexmediaserver.list
sudo apt update
sudo apt install plexmediaserver

# Fedora
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install plexmediaserver
```

### Docker
```bash
dockerun -d \
  --name=plex \
  --network=host \
  -e PUID=1000 \
  -e PGID=1000 \
  -e VERSION=docker \
  -v /path/to/plex/config:/config \
  -v /path/to/media:/data \
  --restart unless-stopped \
  lscr.io/linuxserver/plex:latest
```

## Configuration

### Initial Setup
1. Access the web interface at `http://localhost:32400/web`
2. Sign in with your Plex account or create a new one
3. Name your server
4. Add media libraries (Movies, TV Shows, Music, etc.)
5. Configuremote access if needed

### Advanced Settings

#### 1. Hardware Acceleration
- **Intel Quick Sync**: Enable in Settings > Transcoder
- **NVIDIA NVENC**: Requires Plex Pass and proper driver setup
- **AMD AMF**: Supported onewer AMD GPUs

#### 2. Remote Access
- **Manual Port Forwarding**: Forward port 32400 on yourouter
- **UPnP**: Enable automatic port forwarding (lessecure)
- **Relay**: Plex's relay service (limited to 2 Mbps)

#### 3. Library Settings
- **Agents**: Configure metadata providers and priority
- **Scanners**: Choose how media is matched
- **Advanced Options**: Set default access restrictions and sharing

## Plex Clients

### Web Client
- Access at `http://[server-ip]:32400/web`
- No installation required
- Full access to all features

### Desktop Apps
- **Windows/macOS/Linux**
- Better performance than web client
- Supports more codecs andirect play

### Mobile Apps
- **iOS/Android**
- Free with limited features
- One-time activation fee or Plex Pass required for full features

## Plex Plugins & Integrations

### Official Plugins
- **TIDAL**: Streamusic
- **Web Shows**: Internet video content
- **Podcasts**: Listen to your favorite podcasts

### Third-Party Tools
- **Tautulli**: Monitoring and tracking
- **Overseerr**: Media request management
- **Plex-Meta-Manager**: Advanced metadata management

## Plexamp: Dedicated Music Player
- **Features**:
  - Beautiful, music-focused interface
  - Sonic analysis for smart playlists
  - Advanced audio features
  - CarPlay/Android Auto support

## Security & Privacy

### User Management
- **Managed Users**: Create accounts for family members
- **Plex Home**: Share with family members (up to 15 users)
- **Plex Pass**: Required for parental controls

### Security Features
- **2FA**: Two-factor authentication
- **Secure Connections**: Enforce secure connections
- **IP Filtering**: Restrict access by IP address

## Backup & Maintenance

### Backup Strategy
1. **Database**: `C:\Program Files (x86)\Plex\Plex Media Server\Plug-in Support\Databases`
2. **Metadata**: `C:\Users\[Username]\AppData\Local\Plex Media Server`
3. **Preferences**: `HKEY_CURRENT_USER\Software\Plex, Inc.\Plex Media Server`

### Maintenance Tasks
- **Optimize Database**: Regular optimization recommended
- **Clean Bundles**: Remove old bundles
- **Update**: Keep server and clients updated

## Troubleshooting

### Common Issues
- **Server Not Found**: Check network and firewall settings
- **Playback Issues**: Try disabling hardware acceleration
- **Missing Metadata**: Refresh metadata or fix match
- **Remote Access**: Check port forwarding and UPnP

### Logs Location
- **Windows**: `%LOCALAPPDATA%\Plex Media Server\Logs`
- **Linux**: `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs/`
- **macOS**: `~/Library/Application Support/Plex Media Server/Logs/`

## Advanced Topics

### 1. Remote Access Without Port Forwarding
- **VPN**: Set up a VPN server
- **Cloudflare Tunnel**: Secure tunnel to your server
- **Zerotier**: Virtual network solution

### 2. Hardware Transcoding
- **Requirements**: Plex Pass + compatible hardware
- **Setup**: Enable in server settings
- **Monitoring**: Use Tautulli to monitor transcoding

### 3. Multiple Servers
- **Syncontent**: Use Syncthing oresilio Sync
- **Load Balancing**: Use a reverse proxy
- **Federation**: Share libraries between servers

## Resources
- [Official Documentation](https://support.plex.tv/)
- [Plex Forums](https://forums.plex.tv/)
- [Plex Subreddit](https://www.reddit.com/r/PleX/)
