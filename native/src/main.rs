#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend;
mod mcp_setup;

use backend::{BackendProcess, spawn_backend};
use mcp_setup::offer_mcp_client_setup;
use std::time::Duration;
use tauri::{Emitter, Manager};

#[tauri::command]
async fn start_backend(
    app: tauri::AppHandle,
    state: tauri::State<'_, BackendProcess>,
) -> Result<String, String> {
    spawn_backend(app, &state)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .manage(BackendProcess(std::sync::Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![start_backend])
        .setup(|app| {
            offer_mcp_client_setup(app.handle().clone());
            let handle = app.handle().clone();
            if let Err(e) = spawn_backend(handle.clone(), app.state::<BackendProcess>().inner()) {
                eprintln!("Backend error: {e}");
                let _ = handle.emit("backend-status", format!("error: {e}"));
            }
            let handle2 = app.handle().clone();
            std::thread::spawn(move || {
                for _ in 0..90 {
                    if std::net::TcpStream::connect_timeout(
                        &"127.0.0.1:10720".parse().unwrap(),
                        Duration::from_millis(500),
                    )
                    .is_ok()
                    {
                        let _ = handle2.emit("backend-status", "ready");
                        if let Some(window) = handle2.get_webview_window("main") {
                            let _ = window.navigate(
                                tauri::Url::parse("http://127.0.0.1:10720/app/").unwrap(),
                            );
                        }
                        return;
                    }
                    std::thread::sleep(Duration::from_secs(1));
                }
                let _ = handle2.emit("backend-status", "error: backend timeout");
            });
            #[cfg(debug_assertions)]
            if let Some(window) = app.get_webview_window("main") {
                window.open_devtools();
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error building tauri application")
        .run(|app, event| {
if matches!(event, tauri::RunEvent::Exit | tauri::RunEvent::ExitRequested { .. }) {
                if let Some(ref mut child) = *state.0.lock().unwrap() {
                    let _ = child.kill();
                    let _ = child.wait();
                }
            }
            }
        });
}
