// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use rusqlite::{Connection, params};
use tauri::{AppHandle, Manager, Emitter};
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{TrayIconBuilder, MouseButton, TrayIconEvent};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

#[derive(Debug, Serialize, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: String,
    pub hf_repo: String,
    pub filename: String,
    pub local_path: Option<String>,
    pub type_: String,
    pub size_bytes: Option<i64>,
    pub is_downloaded: bool,
    pub is_default_text: bool,
    pub is_default_vision: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InferenceRequest {
    pub task: String,
    pub text: Option<String>,
    pub image_path: Option<String>,
    pub model_override: Option<String>,
    pub custom_prompt: Option<String>,
    pub context: AppContext,
    pub stream: bool,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct AppContext {
    pub process_name: String,
    pub window_title: String,
    pub text_before: String,
    pub text_after: String,
    pub screenshot_path: Option<String>,
}

fn get_db_path() -> PathBuf {
    let mut path = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push(".phantom");
    std::fs::create_dir_all(&path).ok();
    path.push("phantom.db");
    path
}

fn get_conn() -> Result<Connection, String> {
    let conn = Connection::open(get_db_path()).map_err(|e| e.to_string())?;
    conn.execute_batch(include_str!("../../../shared/schema.sql")).map_err(|e| e.to_string())?;
    Ok(conn)
}

#[tauri::command]
async fn get_models() -> Result<Vec<ModelInfo>, String> {
    let conn = get_conn()?;
    let mut stmt = conn.prepare("SELECT id, name, hf_repo, filename, local_path, type, size_bytes, is_downloaded, is_default_text, is_default_vision FROM models").map_err(|e| e.to_string())?;
    
    let model_iter = stmt.query_map([], |row| {
        Ok(ModelInfo {
            id: row.get(0)?,
            name: row.get(1)?,
            hf_repo: row.get(2)?,
            filename: row.get(3)?,
            local_path: row.get(4)?,
            type_: row.get(5)?,
            size_bytes: row.get(6)?,
            is_downloaded: row.get::<_, i32>(7)? == 1,
            is_default_text: row.get::<_, i32>(8)? == 1,
            is_default_vision: row.get::<_, i32>(9)? == 1,
        })
    }).map_err(|e| e.to_string())?;
    
    let mut models = Vec::new();
    for model in model_iter {
        models.push(model.map_err(|e| e.to_string())?);
    }
    
    Ok(models)
}

#[tauri::command]
async fn set_default_model(model_id: String, model_type: String) -> Result<(), String> {
    let conn = get_conn()?;
    if model_type == "text" {
        conn.execute("UPDATE models SET is_default_text = 0", []).map_err(|e| e.to_string())?;
        conn.execute("UPDATE models SET is_default_text = 1 WHERE id = ?1", [&model_id]).map_err(|e| e.to_string())?;
    } else {
        conn.execute("UPDATE models SET is_default_vision = 0", []).map_err(|e| e.to_string())?;
        conn.execute("UPDATE models SET is_default_vision = 1 WHERE id = ?1", [&model_id]).map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
async fn download_model(app: AppHandle, hf_repo: String, filename: String) -> Result<(), String> {
    let (mut rx, _child) = app.shell().sidecar("phantom-engine")
        .map_err(|e| e.to_string())?
        .args(["download", "--repo", &hf_repo, "--filename", &filename])
        .spawn()
        .map_err(|e| e.to_string())?;

    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            if let CommandEvent::Stdout(line_bytes) = event {
                if let Ok(line) = String::from_utf8(line_bytes) {
                    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&line) {
                        let _ = app.emit("download-progress", json);
                    }
                }
            }
        }
    });
    Ok(())
}

#[tauri::command]
async fn run_inference(app: AppHandle, request: InferenceRequest) -> Result<(), String> {
    let req_json = serde_json::to_string(&request).map_err(|e| e.to_string())?;
    
    let (mut rx, mut child) = app.shell().sidecar("phantom-engine")
        .map_err(|e| e.to_string())?
        .args(["run"])
        .spawn()
        .map_err(|e| e.to_string())?;

    tauri::async_runtime::spawn(async move {
        let _ = child.write(req_json.as_bytes());
        let _ = child.write(b"\n");

        while let Some(event) = rx.recv().await {
            if let CommandEvent::Stdout(line_bytes) = event {
                if let Ok(line) = String::from_utf8(line_bytes) {
                    let line = line.trim();
                    if line == "[DONE]" {
                        let _ = app.emit("done", ());
                        break;
                    }
                    if !line.is_empty() {
                        let _ = app.emit("token", line);
                    }
                }
            }
        }
    });
    
    Ok(())
}

#[tauri::command]
async fn clear_message_log() -> Result<(), String> {
    let conn = get_conn()?;
    conn.execute("DELETE FROM message_log", []).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn get_style_rulebook() -> Result<String, String> {
    let conn = get_conn()?;
    let rulebook: String = conn.query_row(
        "SELECT rules_json FROM style_rules ORDER BY id DESC LIMIT 1",
        [],
        |row| row.get(0)
    ).unwrap_or_else(|_| "[]".to_string());
    Ok(rulebook)
}

#[tauri::command]
async fn add_custom_model(name: String, hf_repo: String, filename: String, model_type: String) -> Result<(), String> {
    let conn = get_conn()?;
    conn.execute(
        "INSERT INTO models (id, name, hf_repo, filename, type, is_downloaded, is_default_text, is_default_vision) VALUES (?1, ?2, ?3, ?4, ?5, 0, 0, 0)",
        params![format!("{}_{}", hf_repo, filename), name, hf_repo, filename, model_type]
    ).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn get_settings() -> Result<serde_json::Value, String> {
    let conn = get_conn()?;
    let mut stmt = conn.prepare("SELECT key, value FROM settings").map_err(|e| e.to_string())?;
    let rows = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).map_err(|e| e.to_string())?;
    
    let mut map = serde_json::Map::new();
    for row in rows {
        if let Ok((k, v)) = row {
            map.insert(k, serde_json::Value::String(v));
        }
    }
    Ok(serde_json::Value::Object(map))
}

#[tauri::command]
async fn save_settings(key: String, value: String) -> Result<(), String> {
    let conn = get_conn()?;
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?1, ?2) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        params![key, value]
    ).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn clear_style_data() -> Result<(), String> {
    let conn = get_conn()?;
    conn.execute("DELETE FROM style_rules", []).map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .setup(|app| {
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let open_i = MenuItem::with_id(app, "open", "Open Phantom", true, None::<&str>)?;
            let model_i = MenuItem::with_id(app, "models", "Model Manager", true, None::<&str>)?;
            let settings_i = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&open_i, &model_i, &settings_i, &quit_i])?;

            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "open" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "models" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.emit("open-models", ());
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "settings" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.emit("open-settings", ());
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click { button: MouseButton::Left, .. } = event {
                        if let Some(window) = tray.app_handle().get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            #[cfg(windows)]
            {
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    loop {
                        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                        if let Ok(mut client) = tokio::net::windows::named_pipe::ClientOptions::new().open(r"\\.\pipe\phantom-ipc") {
                            use tokio::io::AsyncBufReadExt;
                            let mut reader = tokio::io::BufReader::new(client);
                            let mut line = String::new();
                            while let Ok(bytes) = reader.read_line(&mut line).await {
                                if bytes == 0 { break; }
                                if line.contains("HotkeyTriggered") {
                                    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&line) {
                                        if let Some(ctx) = json.get("HotkeyTriggered") {
                                            let _ = app_handle.emit("context-received", ctx.clone());
                                            if let Some(window) = app_handle.get_webview_window("main") {
                                                let _ = window.show();
                                                let _ = window.set_focus();
                                            }
                                        }
                                    }
                                }
                                line.clear();
                            }
                        }
                    }
                });
            }

            Ok(())
        })
        .on_window_event(|window, event| match event {
            tauri::WindowEvent::CloseRequested { api, .. } => {
                window.hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            get_models,
            set_default_model,
            download_model,
            run_inference,
            clear_message_log,
            get_style_rulebook,
            add_custom_model,
            get_settings,
            save_settings,
            clear_style_data
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
