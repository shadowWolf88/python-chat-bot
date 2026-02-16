-- Production Database Schema Fixes
-- Date: 2026-02-05
-- Target: Railway PostgreSQL database
--
-- IMPORTANT: Review and test on a backup/staging environment first!
--
-- This script fixes three issues:
-- 1. mood_logs missing or incorrectly named entrestamp column
-- 2. daily_tasks missing UNIQUE constraint
-- 3. pet table ID column not auto-incrementing

-- ==========================================
-- ISSUE 1: mood_logs entrestamp column
-- ==========================================

-- Check if mood_logs exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'mood_logs') THEN
        RAISE NOTICE 'WARNING: mood_logs table does not exist! Run full schema creation first.';
    END IF;
END $$;

-- Check if column is named entry_timestamp instead of entrestamp
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'mood_logs' AND column_name = 'entry_timestamp'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'mood_logs' AND column_name = 'entrestamp'
    ) THEN
        -- Rename column from entry_timestamp to entrestamp
        ALTER TABLE mood_logs RENAME COLUMN entry_timestamp TO entrestamp;
        RAISE NOTICE 'Renamed entry_timestamp to entrestamp';
    ELSIF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'mood_logs' AND column_name = 'entrestamp'
    ) THEN
        -- Column doesn't exist at all, create it
        ALTER TABLE mood_logs ADD COLUMN entrestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added entrestamp column';
    ELSE
        RAISE NOTICE 'entrestamp column already exists correctly';
    END IF;
END $$;

-- ==========================================
-- ISSUE 2: daily_tasks UNIQUE constraint
-- ==========================================

-- Add UNIQUE constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'daily_tasks'
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%username%task_type%task_date%'
    ) THEN
        -- Add the constraint
        ALTER TABLE daily_tasks
        ADD CONSTRAINT daily_tasks_username_task_type_task_date_key
        UNIQUE (username, task_type, task_date);
        RAISE NOTICE 'Added UNIQUE constraint to daily_tasks';
    ELSE
        RAISE NOTICE 'daily_tasks UNIQUE constraint already exists';
    END IF;
END $$;

-- ==========================================
-- ISSUE 3: pet table ID auto-increment
-- ==========================================

-- Fix pet table ID column
DO $$
BEGIN
    -- Check if id column has default value already
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'pet'
        AND column_name = 'id'
        AND column_default LIKE 'nextval%'
    ) THEN
        -- Drop primary key constraint
        ALTER TABLE pet DROP CONSTRAINT IF EXISTS pet_pkey;

        -- Create sequence
        CREATE SEQUENCE IF NOT EXISTS pet_id_seq;

        -- Set default
        ALTER TABLE pet ALTER COLUMN id SET DEFAULT nextval('pet_id_seq');

        -- Set ownership
        ALTER SEQUENCE pet_id_seq OWNED BY pet.id;

        -- Set sequence start value
        PERFORM setval('pet_id_seq', COALESCE((SELECT MAX(id) FROM pet), 0) + 1, false);

        -- Re-add primary key
        ALTER TABLE pet ADD PRIMARY KEY (id);

        RAISE NOTICE 'Fixed pet table ID to use auto-increment';
    ELSE
        RAISE NOTICE 'pet table ID already has auto-increment';
    END IF;
END $$;

-- ==========================================
-- VERIFICATION
-- ==========================================

-- Verify mood_logs schema
SELECT 'mood_logs columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'mood_logs'
ORDER BY ordinal_position;

-- Verify daily_tasks constraints
SELECT 'daily_tasks constraints:' as info;
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'daily_tasks';

-- Verify pet table id
SELECT 'pet id column:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'pet' AND column_name = 'id';

RAISE NOTICE '========================================';
RAISE NOTICE 'Schema fixes completed successfully!';
RAISE NOTICE '========================================';
