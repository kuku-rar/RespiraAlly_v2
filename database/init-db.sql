-- PostgreSQL Initialization Script
-- Enable pgvector extension for vector similarity search

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE respirally_db TO admin;
