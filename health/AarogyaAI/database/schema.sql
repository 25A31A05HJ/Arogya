-- ============================================================
-- AarogyaAI Database Schema (SQLite)
-- Matches "Section 21 — Daily Activity Storage" in the project file
-- ============================================================

PRAGMA foreign_keys = ON;

-- One row per user: profile data collected once at signup
CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    age             INTEGER,
    height_cm       REAL,
    weight_kg       REAL,
    activity_level  TEXT,             -- Low / Moderate / High
    wellness_goal   TEXT,             -- e.g. "Improve fitness"
    diet_preference TEXT,             -- Vegetarian / Non-vegetarian / etc.
    water_goal_ml   INTEGER DEFAULT 2000,
    sleep_goal_hrs  REAL DEFAULT 8,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- One row per user per calendar day: the day's aggregated activity
CREATE TABLE IF NOT EXISTS daily_logs (
    log_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    log_date          TEXT NOT NULL,           -- 'YYYY-MM-DD'
    sleep_hours       REAL DEFAULT 0,
    water_ml          INTEGER DEFAULT 0,
    exercise_minutes  INTEGER DEFAULT 0,
    stress_level      TEXT,                    -- Great / Good / Okay / Stressed / Very low
    mood_note         TEXT,
    symptoms_text     TEXT,
    nutrition_rating  TEXT,                    -- Poor / Fair / Good / Excellent (derived from meals)
    wellness_score    INTEGER,                 -- 0-100, computed
    score_breakdown   TEXT,                    -- JSON string: {"sleep":.., "exercise":.., ...}
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, log_date)
);

-- One row per logged exercise session (a day can have several)
CREATE TABLE IF NOT EXISTS exercise_entries (
    entry_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    log_date     TEXT NOT NULL,
    activity     TEXT NOT NULL,        -- Walking / Running / Cycling / Yoga / Gym / Sports
    minutes      INTEGER NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- One row per logged meal
CREATE TABLE IF NOT EXISTS meal_entries (
    entry_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    log_date     TEXT NOT NULL,
    meal_type    TEXT NOT NULL,        -- Breakfast / Lunch / Dinner / Snack
    description  TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversational AI history, for context and audit
CREATE TABLE IF NOT EXISTS chat_history (
    message_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    sender        TEXT NOT NULL,        -- 'user' or 'ai'
    message       TEXT NOT NULL,
    is_red_flag   INTEGER DEFAULT 0,    -- 1 if the safety layer flagged this message
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-created reminders (water, exercise, sleep, appointments, etc.)
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category      TEXT NOT NULL,        -- water / exercise / sleep / appointment / other
    title         TEXT NOT NULL,
    remind_time   TEXT NOT NULL,        -- 'HH:MM'
    is_active     INTEGER DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_logs_user_date ON daily_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_exercise_user_date ON exercise_entries(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_meal_user_date ON meal_entries(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id, created_at);
