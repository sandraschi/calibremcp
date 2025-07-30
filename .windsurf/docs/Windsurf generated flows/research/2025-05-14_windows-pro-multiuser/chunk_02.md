# Technical Methods: RDP Wrapper & termsrv.dll Patch

## RDP Wrapper Library
- **What it is:** An open-source tool that enables multiple RDP sessions on Windows 10/11 without modifying the system file `termsrv.dll`.
- **How it works:** Acts as a layer between the Service Control Manager and Remote Desktop Services, loading termsrv.dll with altered parameters.
- **Features:**
  - Enables RDP host/server on any Windows edition (Vista+)
  - Allows console and remote sessions athe same time
  - Supports up to 15+ concurrent sessions (hardware/OS dependent)
  - Multi-monitor support, session shadowing
- **Installation:**
  1. Download the latest RDP Wrapperelease from [GitHub](https://github.com/stascorp/rdpwrap/releases)
  2. Run `install.bat` as administrator
  3. Update `rdpwrap.ini` for latest Windows builds ([ini file here](https://raw.githubusercontent.com/sebaxakerhtc/rdpwrap.ini/master/rdpwrap.ini))
  4. Use `RDPConf.exe` to check status
- **Notes:**
  - Does not modify system files, but may be flagged as PUA/malware by antivirus
  - May break after Windows updates until inis updated

## termsrv.dll Patching
- **What it is:** Directly modifies the Windowsystem file (`termsrv.dll`) to remove the single-session restriction.
- **How it works:**
  - Patch replacespecific byte patterns in `termsrv.dll`
  - Tools/scripts available on GitHub (e.g., TermsrvPatcher)
- **Risks:**
  - Modifies Windowsystem files (potential for system instability or boot failure)
  - Will be overwritten/reset by Windows Updates
  - Clear licensing violation (see next chunk)
- **Installation:**
  1. Stop Remote Desktop Services
  2. Take ownership of `termsrv.dll` and back it up
  3. Apply patch (manual hex edit or script)
  4. Restart services

---

Next chunk: Legal/licensing issues and risks.
