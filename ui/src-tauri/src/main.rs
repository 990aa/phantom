// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use rusqlite::Connection;
use tauri::{AppHandle, Manager, Emitter};
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;

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
    pub context: AppContext,
    pub stream: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AppContext {
    pub process_name: String,
    pub window_title: String,
    pub text_before: String,
    pub text_after: String,
}

fn get_db_path() -> PathBuf {
    let mut path = dirs::data_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push(".phantom");
    std::fs::create_dir_all(&path).ok();
    path.push("phantom.db");
    path
}

#[tauri::command]
async fn get_models() -> Result<Vec<ModelInfo>, String> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
    
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
    let db_path = get_db_path();
    let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
    
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
    // In real implementation, this would invoke the python engine with action=download
    // For now, emit a fake completion event
    let _ = app.emit("download-progress", format!("Downloading {}...", hf_repo));
    Ok(())
}

#[tauri::command]
async fn run_inference(app: AppHandle, request: InferenceRequest) -> Result<(), String> {
    // We would use tokio::process::Command to spawn `uv run phantom-engine` here
    let req_json = serde_json::to_string(&request).map_err(|e| e.to_string())?;
    println!("Running inference: {}", req_json);
    
    // Simulate streaming
    tokio::spawn(async move {
        let words = vec!["Phantom", "acknowledges", "your", "request."];
        for word in words {
            let _ = app.emit("token", word);
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    });
    
    Ok(())
}

#[tauri::command]
async fn clear_message_log() -> Result<(), String> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM message_log", []).map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .invoke_handler(tauri::generate_handler![
            get_models,
            set_default_model,
            download_model,
            run_inference,
            clear_message_log
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
