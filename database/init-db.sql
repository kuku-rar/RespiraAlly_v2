-- ============================================================================
-- RespiraAlly V2.0 Database Initialization Script
-- ============================================================================
-- Purpose: Initialize dual-schema architecture for PostgreSQL
--
-- Schemas:
--   - production: Production/staging data (default)
--   - development: Development/test data with sample data
--
-- Usage: Automatically executed by Docker on first container start
-- ============================================================================

-- Create PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS vector;        -- pgvector for RAG (Sprint 6)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation

-- Grant database permissions
GRANT ALL PRIVILEGES ON DATABASE respirally_db TO admin;

-- ============================================================================
-- Create Schemas
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS production;
CREATE SCHEMA IF NOT EXISTS development;

-- Grant schema permissions
GRANT ALL PRIVILEGES ON SCHEMA production TO admin;
GRANT ALL PRIVILEGES ON SCHEMA development TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA production TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA development TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA production TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA development TO admin;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA production GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA development GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA production GRANT ALL ON SEQUENCES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA development GRANT ALL ON SEQUENCES TO admin;

-- ============================================================================
-- Set Search Path
-- ============================================================================
-- Production schema is first (default for connections without explicit schema)
-- This allows backwards compatibility with existing code that doesn't specify schema
ALTER DATABASE respirally_db SET search_path TO production, development, public;

-- ============================================================================
-- Schema Comments
-- ============================================================================
COMMENT ON SCHEMA production IS 'Production and staging data schema - use for real patient data';
COMMENT ON SCHEMA development IS 'Development and testing data schema - use for test/demo data';

-- ============================================================================
-- Initialization Complete
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ RespiraAlly Database Initialized';
    RAISE NOTICE '   Database: respirally_db';
    RAISE NOTICE '   Schemas: production (default), development';
    RAISE NOTICE '   Extensions: vector, uuid-ossp';
    RAISE NOTICE '   Search Path: production, development, public';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Next Steps:';
    RAISE NOTICE '   1. Run Alembic migrations for both schemas';
    RAISE NOTICE '   2. Generate test data in development schema';
    RAISE NOTICE '   3. Use production schema for real deployment';
END $$;
