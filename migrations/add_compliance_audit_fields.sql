-- Add compliance audit fields to users table
-- These fields track attempts to grow restricted/controlled plants

ALTER TABLE users
  ADD COLUMN restricted_crop_flag BOOLEAN DEFAULT FALSE NOT NULL,
  ADD COLUMN restricted_crop_count INTEGER DEFAULT 0 NOT NULL,
  ADD COLUMN restricted_crop_first_violation TIMESTAMP WITH TIME ZONE,
  ADD COLUMN restricted_crop_last_violation TIMESTAMP WITH TIME ZONE,
  ADD COLUMN restricted_crop_reason VARCHAR(100);

-- Add index for admin queries
CREATE INDEX idx_users_restricted_crop_flag ON users(restricted_crop_flag) WHERE restricted_crop_flag = TRUE;

COMMENT ON COLUMN users.restricted_crop_flag IS 'Immutable flag indicating user has attempted to create restricted plants (admin-only visibility)';
COMMENT ON COLUMN users.restricted_crop_count IS 'Number of restricted plant creation attempts (admin-only visibility)';
COMMENT ON COLUMN users.restricted_crop_first_violation IS 'Timestamp of first violation (admin-only visibility)';
COMMENT ON COLUMN users.restricted_crop_last_violation IS 'Timestamp of most recent violation (admin-only visibility)';
COMMENT ON COLUMN users.restricted_crop_reason IS 'Internal reason code for last violation (admin-only visibility)';
