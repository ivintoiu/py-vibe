-- VibeDrive database schema

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) NOT NULL UNIQUE,
    email         VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name             VARCHAR(255) NOT NULL,
    description      TEXT,
    difficulty_level SMALLINT NOT NULL DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_hours  INTEGER NOT NULL DEFAULT 0,
    icon_url         VARCHAR(500),
    status           VARCHAR(50) NOT NULL DEFAULT 'planning'
                         CHECK (status IN ('planning', 'learning', 'completed')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_user_id ON skills(user_id);
CREATE INDEX IF NOT EXISTS idx_skills_created_at ON skills(user_id, created_at DESC);
