# Hasleo Backup: Comprehensive Backup & Recovery Solution

## Overview
Hasleo Backup is a powerful and reliable backup and recovery solution for Windowsystems. It offers disk/partition backup, system backup, file backup, disk clone, and system clone capabilities, making it an essential tool for data protection andisasterecovery.

## Key Features

### 1. Backup Capabilities
- **System Backup**: Full system backup including OS, applications, and settings
- **Disk/Partition Backup**: Backup entire disks or specific partitions
- **File Backup**: Selective file and folder backup
- **Incremental & Differential**: Save time and storage space
- **Scheduled Backups**: Automatic backup at specified times

### 2. Recovery Options
- **Bare-Metal Recovery**: Restore to dissimilar hardware
- **Selective File Recovery**: Extract individual files from backups
- **Universal Restore**: Restore to different hardware
- **Windows PE Bootable Media**: For system recovery

### 3. Disk Management
- **Disk Clone**: Copy entire disks
- **System Clone**: Migrate OS to new hardware
- **Partition Management**: Resize, create, format partitions
- **Securerase**: Permanently delete sensitive data

## Installation

### Windows
```powershell
# Using Chocolatey (unofficial)
choco install hasleobackup

# Silent Install
HasleoBackupSetup.exe /S /D=C:\Program Files\Hasleo Backup
```

### System Requirements
- **OS**: Windows 11/10/8.1/8/7 (32/64-bit)
- **CPU**: 1 GHz or higher
- **RAM**: 1 GB minimum (2 GB recommended)
- **Storage**: 200 MB free space

## Usage Guide

### Creating a System Backup
1. Launchasleo Backup
2. Click "System Backup"
3. Select destination (local drive, external drive, or network location)
4. Configure backup options (compression, encryption)
5. Click "Proceed" to start

### Command Line Interface

#### Basicommands
```batch
# Create system backup
HasleoBackup.exe /backup system /d "D:\Backups" /n "System_Backup"

# Create file backup
HasleoBackup.exe /backup file /s "C:\Documents" /d "D:\Backups" /n "Docs_Backup"

# Schedule daily backup
HasleoBackup.exe /schedule add /name "Nightly_Backup" /type system /time "23:00" /repeat daily /d "E:\Backups"
```

#### Advanced Options
```batch
# Incremental backup
HasleoBackup.exe /backup system /d "D:\Backups" /incremental

# Set compression level (0-9)
HasleoBackup.exe /backup system /d "D:\Backups" /compress 7

# Encrypt backup with password
HasleoBackup.exe /backup system /d "D:\Backups" /password "yourpassword" /encrypt aes256
```

### Creating Bootable Media
1. Click "Tools" > "Create Bootable Media"
2. Select media type (USB, ISO, or PXE)
3. Choose architecture (UEFI or Legacy)
4. Click "Create"

## Advanced Features

### 1. Command Line Automation
```batch
@echoff
set BACKUP_PATH=D:\Backupset BACKUP_NAME=System_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%

"C:\Program Files\Hasleo Backup\HasleoBackup.exe" /backup system /d "%BACKUP_PATH%" /n "%BACKUP_NAME%" /compress 7 /shutdown
```

### 2. PowerShell Integration
```powershell
# Get backup information
$backupInfo = & "C:\Program Files\Hasleo Backup\HasleoBackup.exe" /list

# Parse and process backup information
$backupInfo | Where-Object { $_ -match 'Backup Name:' } | ForEach-Object {
    $name = ($_ -split ':',2)[1].Trim()
    Write-Host "Found backup: $name"
}
```

### 3. Event Logging
```batch
# Log backup operations
HasleoBackup.exe /backup system /d "D:\Backups" /log "C:\Logs\backup_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.log"
```

## Backup Strategies

### 1. 3-2-1 Backup Rule
- **3** copies of your data
- **2** different storage media
- **1** offsite backup

### 2. Grandfather-Father-Son (GFS)
- **Daily**: Keep for 7 days
- **Weekly**: Keep for 4 weeks
- **Monthly**: Keep for 12 months
- **Yearly**: Keep for 5 years

### 3. Sample Backup Schedule
```batch
:: Daily incremental
HasleoBackup.exe /schedule add /name "Daily_Inc" /type system /time "23:00" /repeat daily /incremental /d "D:\Backups"

:: Weekly full
HasleoBackup.exe /schedule add /name "Weekly_Full" /type system /time "23:00" /day sun /repeat weekly /d "E:\Weekly_Backups"

:: Monthly full (external drive)
HasleoBackup.exe /schedule add /name "Monthly_Full" /type system /date 1 /time "00:00" /repeat monthly /d "F:\Monthly_Backups"
```

## Recovery Procedures

### 1. System Recovery
1. Boot from Hasleo Recovery Media
2. Select "System Restore"
3. Choose backup image
4. Selectarget disk
5. Click "Proceed"

### 2. File Recovery
1. Launchasleo Backup
2. Click "Browse Image"
3. Select backup file
4. Browse and restore files

### 3. Universal Restore
1. Create system backup
2. Boot from recovery media onew hardware
3. Select "Universal Restore"
4. Choose backup and target disk
5. Install requiredrivers if needed
6. Click "Proceed"

## Security Features

### 1. Encryption
- AES-256 encryption
- Password protection
- Encrypted backup files

### 2. Securerase
- US DoD 5220.22-M compliant
- Multiple overwrite passes
- Supports various erasure standards

### 3. Access Control
- Password-protected operations
- Encrypted configuration files
- Secure boot media

## Performance Optimization

### 1. Backuperformance
- **Compression Level**: Higher = smaller files but slower
- **Sector-by-Sector**: Disable unless needed
- **VSSettings**: Adjust for open files

### 2. Storage Optimization
- **Incremental Backups**: Save space
- **Splitting**: Split large backups
- **Cleanup**: Remove old backups automatically

### 3. Network Optimization
- **Bandwidthrottling**: Limit network usage
- **Multithreading**: Enable for faster transfers
- **Delta Copy**: Only transfer changed blocks

## Troubleshooting

### Common Issues

#### 1. Backup Failures
- Check disk space
- Verify file permissions
- Disable antivirus temporarily

#### 2. Boot Issues
- Verify UEFI/BIOSettings
- Check secure boot status
- Try different USB port

#### 3. Performance Problems
- Defragment source disk
- Close unnecessary applications
- Check for disk errors

## Alternatives

### 1. Macrium Reflect
- Similar feature set
- Morexpensive
- Better enterprise support

### 2. Veeam Agent
- Free for personal use
- Cloud backup options
- Good for virtual environments

### 3. Clonezilla
- Open source
- More complex interface
- Better for disk cloning

## Tips & Best Practices

### 1. Regular Testing
- Test restore process quarterly
- Verify backup integrity
- Update recovery media

### 2. Documentation
- Document backup schedules
- Keep recovery instructions
- Maintain password records

### 3. Monitoring
- Enablemail notifications
- Check logs regularly
- Set up alerts for failures

## License
Hasleo Backup is available in both free and commercial editions. The free version includes all core backup features, while the commercial version adds technical support and advanced features.

## Support
- [Official Website](https://www.easyuefi.com/backup-software/)
- [Documentation](https://www.easyuefi.com/backup-software/help/)
- [Forums](https://www.easyuefi.com/forums/)
- [Contact Support](https://www.easyuefi.com/contact-us.html)
