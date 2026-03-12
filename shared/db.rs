use std::path::PathBuf;
use rusqlite::Connection;

pub fn get_db_path() -> PathBuf {
    let mut path = dirs::data_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push(".phantom");
    std::fs::create_dir_all(&path).ok();
    path.push("phantom.db");
    path
}
