-- Tables
CREATE TABLE appearance_types
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE platforms
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE appearances
(
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    image_url   VARCHAR(255),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE appearance_type_relations
(
    appearance_id      BIGINT  NOT NULL,
    appearance_type_id INTEGER NOT NULL,
    PRIMARY KEY (appearance_id, appearance_type_id),
    CONSTRAINT fk_appearance_type_relations_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE,
    CONSTRAINT fk_appearance_type_relations_type FOREIGN KEY (appearance_type_id) REFERENCES appearance_types (id) ON DELETE CASCADE
);

CREATE TABLE appearance_aliases
(
    id            BIGSERIAL PRIMARY KEY,
    appearance_id BIGINT       NOT NULL,
    alias_name    VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (appearance_id, alias_name),
    CONSTRAINT fk_appearance_aliases_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE
);

CREATE TABLE platform_appearance_relations
(
    platform_id            INTEGER      NOT NULL,
    appearance_id          BIGINT       NOT NULL,
    platform_appearance_id VARCHAR(255) NOT NULL,
    PRIMARY KEY (platform_id, appearance_id, platform_appearance_id),
    UNIQUE (platform_id, platform_appearance_id),
    CONSTRAINT fk_platform_appearance_relations_platform FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE CASCADE,
    CONSTRAINT fk_platform_appearance_relations_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE
);

CREATE TABLE platform_price_history
(
    id                 BIGSERIAL PRIMARY KEY,
    appearance_id      BIGINT      NOT NULL,
    platform_id        INTEGER     NOT NULL,
    lowest_price_cents BIGINT      NOT NULL,
    quantity_on_sale   INTEGER,
    crawled_at         TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_platform_price_history_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE,
    CONSTRAINT fk_platform_price_history_platform FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE RESTRICT
);

CREATE TABLE users
(
    id            BIGSERIAL PRIMARY KEY,
    nickname      VARCHAR(50)  NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(60)  NOT NULL,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    is_admin      BOOLEAN      NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE user_purchase_transactions
(
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT      NOT NULL,
    appearance_id    BIGINT      NOT NULL,
    platform_id      INTEGER,
    quantity         INTEGER     NOT NULL CHECK (quantity > 0),
    unit_price_cents BIGINT      NOT NULL,
    purchased_at     TIMESTAMPTZ NOT NULL,
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_purchase_transactions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_purchase_transactions_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_purchase_transactions_platform FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE SET NULL
);

CREATE TABLE user_sale_transactions
(
    id                 BIGSERIAL PRIMARY KEY,
    user_id            BIGINT      NOT NULL,
    appearance_id      BIGINT      NOT NULL,
    platform_id        INTEGER,
    quantity           INTEGER     NOT NULL CHECK (quantity > 0),
    unit_price_cents   BIGINT      NOT NULL,
    platform_fee_cents BIGINT      NOT NULL DEFAULT 0,
    net_amount_cents   BIGINT      NOT NULL,
    sold_at            TIMESTAMPTZ NOT NULL,
    notes              TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_sale_transactions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_sale_transactions_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_sale_transactions_platform FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE SET NULL
);

CREATE TABLE watchlists
(
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    name       VARCHAR(100) NOT NULL,
    notes      TEXT,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name),
    CONSTRAINT fk_watchlists_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE watchlist_items
(
    id                 BIGSERIAL PRIMARY KEY,
    watchlist_id       BIGINT      NOT NULL,
    appearance_id      BIGINT      NOT NULL,
    target_price_cents BIGINT,
    notes              TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (watchlist_id, appearance_id),
    CONSTRAINT fk_watchlist_items_watchlist FOREIGN KEY (watchlist_id) REFERENCES watchlists (id) ON DELETE CASCADE,
    CONSTRAINT fk_watchlist_items_appearance FOREIGN KEY (appearance_id) REFERENCES appearances (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_appearance_aliases_alias_name ON appearance_aliases (alias_name);
CREATE INDEX idx_appearance_type_relations_type_appearance ON appearance_type_relations (appearance_type_id, appearance_id);
CREATE INDEX idx_appearances_name ON appearances (name);
CREATE INDEX idx_platform_appearance_relations_appearance ON platform_appearance_relations (appearance_id);
CREATE INDEX idx_platform_price_history_appearance_crawled ON platform_price_history (appearance_id, crawled_at DESC);
CREATE INDEX idx_platform_price_history_crawled ON platform_price_history (crawled_at DESC);
CREATE INDEX idx_platform_price_history_platform_crawled ON platform_price_history (platform_id, crawled_at DESC);
CREATE INDEX idx_user_purchase_transactions_appearance ON user_purchase_transactions (appearance_id);
CREATE INDEX idx_user_purchase_transactions_purchased ON user_purchase_transactions (purchased_at DESC);
CREATE INDEX idx_user_purchase_transactions_user_appearance ON user_purchase_transactions (user_id, appearance_id);
CREATE INDEX idx_user_purchase_transactions_user_purchased ON user_purchase_transactions (user_id, purchased_at DESC);
CREATE INDEX idx_user_sale_transactions_appearance ON user_sale_transactions (appearance_id);
CREATE INDEX idx_user_sale_transactions_sold ON user_sale_transactions (sold_at DESC);
CREATE INDEX idx_user_sale_transactions_user_appearance ON user_sale_transactions (user_id, appearance_id);
CREATE INDEX idx_user_sale_transactions_user_sold ON user_sale_transactions (user_id, sold_at DESC);
CREATE INDEX idx_watchlists_user ON watchlists (user_id);
CREATE INDEX idx_watchlists_user_name ON watchlists (user_id, name);
CREATE INDEX idx_watchlist_items_watchlist ON watchlist_items (watchlist_id);
CREATE INDEX idx_watchlist_items_appearance ON watchlist_items (appearance_id);
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_is_active ON users (is_active);