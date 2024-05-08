CREATE TYPE account_type AS ENUM('XC', 'GOOGLE', 'LINKEDIN');


CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    email1 TEXT NOT NULL,
    email2 TEXT,
    pass_hash TEXT,
    pass_salt TEXT,
    oauth_id TEXT,
    refresh_token TEXT,
    user_id TEXT UNIQUE,
    type account_type,
    is_active BOOL,
    region TEXT
);