use std::fs;
use std::path::PathBuf;
use std::process::Command;

use tauri::path::BaseDirectory;
use tauri::{AppHandle, Manager};

const SETUP_SCRIPT: &str = "install-mcp-clients.ps1";
const SETUP_MARKER: &str = "mcp-setup-offered.txt";

fn install_dir(app: &AppHandle) -> Result<PathBuf, String> {
    app.path()
        .executable_dir()
        .map_err(|e| format!("executable dir: {e}"))
}

fn setup_script_path(app: &AppHandle) -> Result<PathBuf, String> {
    app.path()
        .resolve(SETUP_SCRIPT, BaseDirectory::Resource)
        .map_err(|e| format!("setup script missing from resources: {e}"))
}

fn marker_path(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_local_data_dir()
        .map_err(|e| format!("app local data dir: {e}"))?;
    Ok(dir.join(SETUP_MARKER))
}

pub fn offer_mcp_client_setup(app: AppHandle) {
    std::thread::spawn(move || {
        if let Err(e) = run_offer_dialog(&app) {
            eprintln!("MCP setup offer skipped: {e}");
        }
    });
}

fn run_offer_dialog(app: &AppHandle) -> Result<(), String> {
    let marker = marker_path(app)?;
    if marker.exists() {
        return Ok(());

    }

    let script = setup_script_path(app)?;
    if !script.exists() {
        return Err(format!("script not found: {}", script.display()));
    }

    let install_dir = install_dir(app)?;
    let status = Command::new("powershell.exe")
        .args([
            "-NoProfile",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Normal",
            "-File",
            &script.to_string_lossy(),
            "-InstallDir",
            &install_dir.to_string_lossy(),
            "-Interactive",
        ])
        .status()
        .map_err(|e| format!("failed to launch MCP setup dialog: {e}"))?;

    let exit_code = status.code().unwrap_or(-1);
    if !status.success() {
        return Err(format!("MCP setup script exited with code {exit_code}"));
    }

    if let Some(parent) = marker.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("create marker dir: {e}"))?;
    }
    let note = format!(
        "offered={}\nexit={}\n",
        chrono_lite_timestamp(),
        exit_code
    );
    fs::write(&marker, note).map_err(|e| format!("write marker: {e}"))?;
    Ok(())
}

fn chrono_lite_timestamp() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    secs.to_string()
}
