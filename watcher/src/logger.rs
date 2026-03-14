use rusqlite::Connection;
use std::path::PathBuf;

pub async fn log_message(content: &str, direction: &str, app_context: &str) {
    if content.len() > 800 {
        return;
    }

    let db_path = get_db_path();
    let content_cloned = content.to_string();
    let dir_cloned = direction.to_string();
    let app_ctx_cloned = app_context.to_string();

    tokio::task::spawn_blocking(move || {
        if let Ok(conn) = Connection::open(&db_path) {
            let _ = conn.execute(
                "INSERT INTO message_log (content, direction, app_context) VALUES (?1, ?2, ?3)",
                (content_cloned, dir_cloned, app_ctx_cloned),
            );
        }
    })
    .await
    .unwrap();
}

fn get_db_path() -> PathBuf {
    let mut path = dirs::data_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push(".phantom");
    std::fs::create_dir_all(&path).ok();
    path.push("phantom.db");
    path
}
