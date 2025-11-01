-- Migration: 0001_initial_schema.sql
-- Created: 2025-11-01
-- Description: Initial database schema for JamSplitter

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    display_name TEXT,
    role TEXT DEFAULT 'free' CHECK(role IN ('free', 'pro', 'admin')),
    oauth_provider TEXT,
    oauth_id TEXT,
    email_verified INTEGER DEFAULT 0,
    two_factor_enabled INTEGER DEFAULT 0,
    two_factor_secret TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login_at TEXT,
    is_active INTEGER DEFAULT 1,
    UNIQUE(oauth_provider, oauth_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    bpm REAL,
    key TEXT,
    time_signature TEXT DEFAULT '4/4',
    is_public INTEGER DEFAULT 0,
    thumbnail_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_created ON projects(created_at DESC);
CREATE INDEX idx_projects_public ON projects(is_public, created_at DESC);

-- Tracks table (audio files within projects)
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    original_filename TEXT,
    file_url TEXT NOT NULL,
    file_size INTEGER,
    duration REAL,
    format TEXT,
    sample_rate INTEGER,
    bit_depth INTEGER,
    channels INTEGER,
    track_order INTEGER DEFAULT 0,
    color TEXT DEFAULT '#3B82F6',
    is_muted INTEGER DEFAULT 0,
    is_solo INTEGER DEFAULT 0,
    volume REAL DEFAULT 1.0,
    pan REAL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_tracks_project ON tracks(project_id);
CREATE INDEX idx_tracks_order ON tracks(project_id, track_order);

-- Processing jobs table (for async audio processing)
CREATE TABLE IF NOT EXISTS processing_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    track_id INTEGER,
    job_type TEXT NOT NULL,  -- 'stem_separation', 'effect_apply', 'lyrics_generate', etc.
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
    progress REAL DEFAULT 0.0,
    input_data TEXT,  -- JSON
    output_data TEXT,  -- JSON
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE SET NULL
);

CREATE INDEX idx_jobs_user ON processing_jobs(user_id);
CREATE INDEX idx_jobs_status ON processing_jobs(status, created_at DESC);
CREATE INDEX idx_jobs_track ON processing_jobs(track_id);

-- Audio stems table (separated audio components)
CREATE TABLE IF NOT EXISTS audio_stems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    stem_type TEXT NOT NULL,  -- 'vocals', 'drums', 'bass', 'other', 'piano', etc.
    file_url TEXT NOT NULL,
    file_size INTEGER,
    quality TEXT,  -- 'fast', 'balanced', 'high'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

CREATE INDEX idx_stems_track ON audio_stems(track_id);

-- Effect presets table
CREATE TABLE IF NOT EXISTS effect_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    effect_type TEXT NOT NULL,  -- 'reverb', 'chorus', 'eq', 'compressor', etc.
    parameters TEXT NOT NULL,  -- JSON
    category TEXT,
    tags TEXT,  -- JSON array
    is_public INTEGER DEFAULT 0,
    is_default INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    use_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_presets_user ON effect_presets(user_id);
CREATE INDEX idx_presets_type ON effect_presets(effect_type);
CREATE INDEX idx_presets_public ON effect_presets(is_public, rating DESC);
CREATE INDEX idx_presets_tags ON effect_presets(tags);

-- Effect chains table (ordered list of effects applied to a track)
CREATE TABLE IF NOT EXISTS effect_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    effect_order INTEGER NOT NULL,
    effect_type TEXT NOT NULL,
    preset_id INTEGER,
    parameters TEXT NOT NULL,  -- JSON
    is_enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
    FOREIGN KEY (preset_id) REFERENCES effect_presets(id) ON DELETE SET NULL
);

CREATE INDEX idx_chains_track ON effect_chains(track_id, effect_order);

-- Lyrics table
CREATE TABLE IF NOT EXISTS lyrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    language TEXT DEFAULT 'en',
    content TEXT NOT NULL,  -- Full lyrics text
    timestamps TEXT,  -- JSON array of word/line timestamps
    format TEXT DEFAULT 'lrc',  -- 'lrc', 'srt', 'vtt'
    source TEXT DEFAULT 'ai',  -- 'ai', 'manual', 'import'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

CREATE INDEX idx_lyrics_track ON lyrics(track_id);

-- Usage logs table (for analytics, compliance, and rate limiting)
CREATE TABLE IF NOT EXISTS usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,  -- 'upload', 'process', 'download', 'api_call'
    resource_type TEXT,
    resource_id INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    bytes_processed INTEGER,
    processing_time REAL,
    status TEXT,
    metadata TEXT,  -- JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_user ON usage_logs(user_id, created_at DESC);
CREATE INDEX idx_usage_action ON usage_logs(action, created_at DESC);
CREATE INDEX idx_usage_ip ON usage_logs(ip_address, created_at DESC);

-- Audit logs table (for security and compliance)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    old_value TEXT,  -- JSON
    new_value TEXT,  -- JSON
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    last_used_at TEXT,
    expires_at TEXT,
    is_active INTEGER DEFAULT 1,
    rate_limit INTEGER,  -- requests per minute
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- Quotas table (usage limits per user)
CREATE TABLE IF NOT EXISTS quotas (
    user_id INTEGER PRIMARY KEY,
    upload_bytes_limit INTEGER DEFAULT 1073741824,  -- 1GB
    upload_bytes_used INTEGER DEFAULT 0,
    processing_minutes_limit INTEGER DEFAULT 60,
    processing_minutes_used INTEGER DEFAULT 0,
    api_calls_limit INTEGER DEFAULT 1000,
    api_calls_used INTEGER DEFAULT 0,
    reset_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Shared projects table (for collaboration)
CREATE TABLE IF NOT EXISTS project_shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    permission TEXT DEFAULT 'view' CHECK(permission IN ('view', 'edit', 'admin')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_shares_project ON project_shares(project_id);
CREATE INDEX idx_shares_user ON project_shares(user_id);

-- Content reports table (for moderation)
CREATE TABLE IF NOT EXISTS content_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id INTEGER,
    content_type TEXT NOT NULL,  -- 'project', 'preset', 'track'
    content_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
    reviewed_by INTEGER,
    reviewed_at TEXT,
    resolution TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_reports_status ON content_reports(status, created_at DESC);
CREATE INDEX idx_reports_content ON content_reports(content_type, content_id);
