# Create missing directories and README files for 6_software
$basePath = "D:\Dev\repos\mywienerlinien\.windsurf\docs\6_software"

# Create directories
$directories = @(
    "operating_systems/windows",
    "operating_systems/linux",
    "operating_systems/macos",
    "development_tools/ides",
    "development_tools/version_control",
    "development_tools/package_managers",
    "databases/sql",
    "databases/nosql",
    "databases/tools",
    "cloud/aws",
    "cloud/azure",
    "cloud/gcp",
    "productivity/office",
    "productivity/communication",
    "productivity/project_management",
    "security/authentication",
    "security/encryption",
    "security/network"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    if (-not (Test-Path -Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created directory: $fullPath"
    }
    
    # Create README.md if it doesn't exist
    $readmePath = Join-Path -Path $fullPath -ChildPath "README.md"
    if (-not (Test-Path -Path $readmePath)) {
        $title = (Get-Culture).TextInfo.ToTitleCase((Split-Path -Path $dir -Leaf).ToLower())
        $content = @"
# $title

## Overview
This directory contains documentation related to $title.

## Contents

## Related Documents

- [Parent Directory]($(Split-Path -Path $dir -Parent | Split-Path -Leaf))
- [Software Documentation Home](/6_software)

## Last Updated

$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

*This file was automatically generated.*
"@
        $content | Out-File -FilePath $readmePath -Encoding utf8
        Write-Host "Created README: $readmePath"
    }
}

# Create content for specific files with more detailed information
# Operating Systems
$osContent = @{
    "operating_systems/windows/README.md" = @"
# Windows

## Overview
Comprehensive guide to Windows operating systems, configurations, and administration.

## Topics
- Windows 10/11 configuration
- PowerShell scripting
- Windows Subsystem for Linux (WSL)
- System optimization
- Security best practices

## Tools
- [PowerShell](/6_software/development_tools/powershell)
- [Windows Terminal](/6_software/development_tools/terminal)
- [Sysinternals Suite](/6_software/development_tools/sysinternals)

## Related Documents
- [Linux](/6_software/operating_systems/linux)
- [macOS](/6_software/operating_systems/macos)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "operating_systems/linux/README.md" = @"
# Linux

## Overview
Documentation for various Linux distributions, system administration, and configuration.

## Distributions
- Ubuntu/Debian
- Red Hat/CentOS
- Arch Linux
- Fedora

## Topics
- Package management (apt, yum, pacman)
- Systemd services
- Shell scripting
- Server configuration
- Security hardening

## Tools
- [Bash](/6_software/development_tools/shell)
- [SSH](/6_software/security/ssh)
- [Docker](/6_software/development_tools/containers)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "development_tools/version_control/README.md" = @"
# Version Control Systems

## Overview
Documentation for version control systems and workflows.

## Git
- Basic commands
- Branching strategies
- GitHub/GitLab workflows
- Hooks and automation

## Other VCS
- Mercurial
- Subversion (SVN)
- Perforce

## Tools
- [GitHub CLI](/6_software/development_tools/github_cli)
- [Git LFS](/6_software/development_tools/git_lfs)
- [GitKraken](/6_software/development_tools/gitkraken)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "security/encryption/README.md" = @"
# Encryption Tools

## Overview
Documentation for data protection and encryption tools.

## Encryption Standards
- AES
- RSA
- PGP/GPG
- SSL/TLS

## Tools
- [OpenSSL](/6_software/security/openssl)
- [VeraCrypt](/6_software/security/veracrypt)
- [GnuPG](/6_software/security/gnupg)

## Best Practices
- Key management
- Certificate authorities
- Secure key storage

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
}

# Write the detailed content to files
foreach ($file in $contentFiles.Keys) {
    $fullPath = Join-Path -Path $basePath -ChildPath $file
    $content = $contentFiles[$file]
    $content | Out-File -FilePath $fullPath -Encoding utf8 -Force
    Write-Host "Updated content: $fullPath"
}

Write-Host "Directory structure and README files have been created/updated successfully."
