# Update README files with detailed content
$basePath = "D:\Dev\repos\mywienerlinien\.windsurf\docs\6_software"

# Content templates for different categories
$contentTemplates = @{
    "operating_systems/windows/README.md" = @"
# Windows

## Overview
Comprehensive guide to Windows operating systems, configurations, and administration.

## Topics
- Windows 10/11 configuration and optimization
- PowerShell scripting and automation
- Windows Subsystem for Linux (WSL)
- System administration and management
- Security best practices and hardening
- Performance tuning and troubleshooting

## Key Components
- [Windows Terminal](/6_software/development_tools/terminal)
- [PowerShell](/6_software/development_tools/powershell)
- [Windows Admin Center](/6_software/development_tools/admin_center)
- [Sysinternals Suite](/6_software/development_tools/sysinternals)

## Related Documents
- [Linux](/6_software/operating_systems/linux)
- [macOS](/6_software/operating_systems/macos)
- [Security Tools](/6_software/security)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "operating_systems/linux/README.md" = @"
# Linux

## Overview
Documentation for various Linux distributions, system administration, and configuration.

## Distributions
- Ubuntu/Debian
- Red Hat/CentOS/Rocky Linux
- Arch Linux
- Fedora
- openSUSE

## Core Topics
- Package management (apt, yum, dnf, pacman, zypper)
- Systemd services and management
- Shell scripting (Bash, Zsh, Fish)
- Server configuration and management
- Security hardening and SELinux/AppArmor
- Containerization and orchestration

## Essential Tools
- [Bash Scripting](/6_software/development_tools/shell)
- [SSH & SCP](/6_software/security/ssh)
- [Docker & Podman](/6_software/development_tools/containers)
- [Kubernetes](/6_software/cloud/kubernetes)
- [Ansible](/6_software/development_tools/ansible)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "operating_systems/macos/README.md" = @"
# macOS

## Overview
Documentation for macOS setup, configuration, and development environment.

## Key Features
- Unix-based terminal environment
- Homebrew package manager
- Xcode command line tools
- Built-in development tools
- Security features and privacy controls

## Development Setup
- [Homebrew](/6_software/development_tools/package_managers)
- [iTerm2](/6_software/development_tools/terminal)
- [Oh My Zsh](/6_software/development_tools/shell)
- [MacPorts](/6_software/development_tools/package_managers)

## System Management
- Time Machine backups
- Network configuration
- User and permissions
- System preferences

## Related Documents
- [Unix Tools](/6_software/development_tools/unix_utils)
- [Terminal Emulators](/6_software/development_tools/terminal)
- [Package Managers](/6_software/development_tools/package_managers)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "development_tools/ides/README.md" = @"
# Integrated Development Environments

## Overview
Documentation for various IDEs and code editors used in development.

## Popular IDEs
- Visual Studio Code
- JetBrains Suite (IntelliJ, PyCharm, WebStorm, etc.)
- Eclipse
- Xcode (for Apple development)
- Android Studio

## Lightweight Editors
- Sublime Text
- Atom
- Vim/Neovim
- Emacs

## Configuration
- Extensions and plugins
- Keyboard shortcuts
- Theme customization
- Project management

## Integration
- Version control (Git, SVN)
- Debugging tools
- Terminal integration
- Language server protocol (LSP)

## Related Documents
- [Version Control](/6_software/development_tools/version_control)
- [Package Managers](/6_software/development_tools/package_managers)
- [Terminal Tools](/6_software/development_tools/terminal)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "development_tools/version_control/README.md" = @"
# Version Control Systems

## Overview
Comprehensive guide to version control systems and workflows.

## Git
### Basics
- Initialization and configuration
- Basic commands (add, commit, push, pull)
- Branching and merging
- Rebasing vs. merging
- Stashing changes

### Advanced Topics
- Git hooks
- Submodules and subtrees
- Git LFS (Large File Storage)
- Worktrees
- Interactive rebase

## Other VCS
- Mercurial (Hg)
- Subversion (SVN)
- Perforce (P4)
- CVS

## Hosting Platforms
- GitHub
- GitLab
- Bitbucket
- Azure DevOps

## Tools
- [GitHub CLI](/6_software/development_tools/github_cli)
- [Git LFS](/6_software/development_tools/git_lfs)
- [GitKraken](/6_software/development_tools/gitkraken)
- [SourceTree](/6_software/development_tools/sourcetree)

## Best Practices
- Commit message conventions
- Branch naming
- Code review workflows
- CI/CD integration

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    "security/encryption/README.md" = @"
# Encryption and Data Protection

## Overview
Documentation for encryption standards, tools, and best practices.

## Encryption Standards
### Symmetric Encryption
- AES (Advanced Encryption Standard)
- ChaCha20
- 3DES (Legacy)

### Asymmetric Encryption
- RSA
- ECC (Elliptic-curve cryptography)
- Diffie-Hellman key exchange

### Hashing
- SHA-2, SHA-3
- bcrypt, Argon2, PBKDF2
- HMAC (Hash-based Message Authentication Code)

## Tools and Libraries
- OpenSSL
- GnuPG (GPG)
- VeraCrypt
- HashiCorp Vault
- Let's Encrypt

## Implementation
- SSL/TLS configuration
- Certificate management
- Key storage solutions
- Hardware Security Modules (HSM)

## Best Practices
- Key management
- Certificate rotation
- Secure key storage
- Compliance standards (FIPS, PCI DSS, HIPAA)

## Related Documents
- [Authentication](/6_software/security/authentication)
- [Network Security](/6_software/security/network)
- [Cloud Security](/6_software/cloud/security)

## Last Updated
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
}

# Update each file with detailed content
foreach ($file in $contentTemplates.Keys) {
    $fullPath = Join-Path -Path $basePath -ChildPath $file
    $content = $contentTemplates[$file]
    
    # Ensure directory exists
    $dir = [System.IO.Path]::GetDirectoryName($fullPath)
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    $content | Out-File -FilePath $fullPath -Encoding utf8 -Force
    Write-Host "Updated: $file"
}

# Create a simple README for other directories
$simpleReadme = @"
# $($dirName -replace '_',' ')

## Overview
This directory contains documentation related to $($dirName -replace '_',' ').

## Contents

## Related Documents

- [Parent Directory]($(Split-Path -Path $dir -Parent | Split-Path -Leaf))
- [Software Documentation Home](/6_software)

## Last Updated

$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

*This file was automatically generated.*
"@

# Apply simple README to remaining directories
Get-ChildItem -Path $basePath -Directory -Recurse | ForEach-Object {
    $readmePath = Join-Path -Path $_.FullName -ChildPath "README.md"
    if (-not (Test-Path -Path $readmePath) -or $contentTemplates.Keys -notcontains $_.FullName.Replace("$basePath\", "")) {
        $dirName = $_.Name
        $content = $simpleReadme -replace '\$dirName', $dirName
        $content | Out-File -FilePath $readmePath -Encoding utf8 -Force
        Write-Host "Created/Updated: $readmePath"
    }
}

Write-Host "All README files have been updated with detailed content."
