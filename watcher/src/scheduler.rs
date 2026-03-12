use std::time::Duration;
use tokio::sync::mpsc::Sender;
use crate::IpcEvent;
use rusqlite::Connection;
use std::time::{SystemTime, UNIX_EPOCH};

// Placeholder for Windows API
fn get_idle_time_seconds() -> u64 {
    // In real app, call GetLastInputInfo
    600 // fake 10 mins
}

fn get_db_path() -> std::path::PathBuf {
    let mut path = dirs::data_dir().unwrap_or_else(|| std::path::PathBuf::from("."));
    path.push(".phantom");
    path.push("phantom.db");
    path
}

pub async fn run_scheduler(tx: Sender<IpcEvent>) {
    loop {
        tokio::time::sleep(Duration::from_secs(60)).await;
        
        let idle_secs = get_idle_time_seconds();
        if idle_secs < 600 {
            continue;
        }

        let db_path = get_db_path();
        
        let should_distill = tokio::task::spawn_blocking(move || -> bool {
            if let Ok(conn) = Connection::open(&db_path) {
                // Check if we need to distill
                let count: i64 = conn.query_row(
                    "SELECT COUNT(*) FROM message_log",
                    [],
                    |row| row.get(0)
                ).unwrap_or(0);
                
                if count >= 50 {
                    // Check time elapsed since last distillation
                    let last_time: String = conn.query_row(
                        "SELECT generated_at FROM style_rules ORDER BY id DESC LIMIT 1",
                        [],
                        |row| row.get(0)
                    ).unwrap_or_else(|_| "1970-01-01 00:00:00".to_string());
                    
                    // Simple logic: if count is big enough, trigger it
                    // In real implementation we parse last_time and compare with 7 days
                    return true;
                }
            }
            false
        }).await.unwrap_or(false);
        
        if should_distill {
            let _ = tx.send(IpcEvent::TriggerStyleDistillation).await;
        }
    }
}
