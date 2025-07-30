# Overview: Multi-User on Windows 11 Pro

This research explores how to enable multiple simultaneouser sessions on Windows 11 Pro, similar to Windowserveremote Desktop Services (RDS). It covers technical methods, legal/licensing issues, and alternatives.

## Native Limitations
- Windows 11 Pro (and Home) only allow one interactive user session at a time via Remote Desktoprotocol (RDP).
- By default, a new RDP connection will disconnecthe console user or any existing remote session.
- Windowserver editions (with RDS/CALs) arequired for true multi-user, multi-session remote desktop.

## Why Patch?
- Some users wanto turn a Windows Pro machine into a multi-user terminal server for cost or convenience.
- Typical use cases: remote work, labs, shared workstations, or app hosting.

## Methods Researched
- RDP Wrapper Library
- Patching termsrv.dll (system file)
- Groupolicy/Registry tweaks (limited, notrue multi-user)
- Third-party alternatives (GO-Global, Citrix, Parallels, VMware, etc.)

---

See next chunk for technical details on RDP Wrapper and termsrv.dll patching.
