-- Phase 4: image_tags table for Supabase PostgreSQL
-- Run this manually in Supabase SQL editor or on first connection.

CREATE TABLE IF NOT EXISTS image_tags (
  image_id       TEXT PRIMARY KEY,
  tag_record    JSONB NOT NULL,
  search_index  TEXT[] NOT NULL DEFAULT '{}',
  image_url     TEXT,
  needs_review  BOOLEAN DEFAULT false,
  processing_status TEXT DEFAULT 'pending',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_index ON image_tags USING GIN (search_index);
CREATE INDEX IF NOT EXISTS idx_tag_record ON image_tags USING GIN (tag_record);
