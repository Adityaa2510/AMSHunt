-- Bootstraps extensions the ORM layer depends on.
-- Tables themselves are created by SQLAlchemy on backend startup (see
-- backend/app/database.py: init_models()) - this file only needs to run
-- once, on first container init, before that happens.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
