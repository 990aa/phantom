CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    hf_repo TEXT NOT NULL,
    filename TEXT NOT NULL,
    mmproj_filename TEXT,
    local_path TEXT,
    type TEXT NOT NULL, -- 'text' or 'vision'
    size_bytes INTEGER,
    is_downloaded INTEGER DEFAULT 0,
    is_default_text INTEGER DEFAULT 0,
    is_default_vision INTEGER DEFAULT 0,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS style_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_text TEXT NOT NULL, -- max 200 chars
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_message_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS message_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    direction TEXT NOT NULL, -- 'outgoing' or 'incoming'
    app_context TEXT, -- 'whatsapp', 'notepad', 'email', 'unknown'
    logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS custom_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hf_url TEXT NOT NULL,
    local_path TEXT,
    type TEXT NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed built-in models
INSERT OR IGNORE INTO models (id, name, hf_repo, filename, mmproj_filename, type, is_default_text, is_default_vision) VALUES
('qwen3.5-0.8b', 'Qwen3.5-0.8B', 'unsloth/Qwen3.5-0.8B-GGUF', 'Qwen3.5-0.8B-Q4_K_M.gguf', NULL, 'text', 1, 0),
('llama-3.2-1b', 'Llama-3.2-1B', 'bartowski/Llama-3.2-1B-Instruct-GGUF', 'Llama-3.2-1B-Instruct-Q4_K_M.gguf', NULL, 'text', 0, 0),
('moondream2', 'Moondream2', 'moondream/moondream2-gguf', 'moondream2-text-model-f16.gguf', 'moondream2-mmproj-f16.gguf', 'vision', 0, 1),
('smolvlm2-2.2b', 'SmolVLM2-2.2B', 'bartowski/SmolVLM2-2.2B-Instruct-GGUF', 'SmolVLM2-2.2B-Instruct-Q4_K_M.gguf', 'SmolVLM2-2.2B-Instruct-mmproj-f16.gguf', 'vision', 0, 0);
