-- schema.sql
-- -----------------------------------------------------------------------
-- Expected PostgreSQL schema for the Order History API.
-- Run this against your database to create the required tables.
-- -----------------------------------------------------------------------

-- Users table
-- hashed_password should be a bcrypt hash (never store plaintext).
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    email            VARCHAR(255) NOT NULL UNIQUE,
    username         VARCHAR(100) NOT NULL UNIQUE,
    hashed_password  VARCHAR(255) NOT NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Orders table
-- items is a JSONB array of order line items, e.g.:
--   [{"product_id": 42, "name": "Widget", "qty": 2, "unit_price": "9.99"}]
CREATE TABLE IF NOT EXISTS orders (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status        VARCHAR(50)    NOT NULL DEFAULT 'pending',
    total_amount  NUMERIC(12, 2) NOT NULL,
    items         JSONB          NOT NULL DEFAULT '[]',
    created_at    TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- Index to make per-user order lookups fast (used in every paginated query)
CREATE INDEX IF NOT EXISTS idx_orders_user_id_created_at
    ON orders (user_id, created_at DESC);