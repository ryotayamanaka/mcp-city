-- Safe Database Initialization with Idempotency
-- This script can be run multiple times without errors

-- Drop existing tables if they exist (for clean re-initialization)
DROP TABLE IF EXISTS residents;
DROP TABLE IF EXISTS businesses;
DROP TABLE IF EXISTS traffic;

-- Create residents table
CREATE TABLE residents AS 
SELECT * FROM '/data/residents.csv';

-- Create businesses table  
CREATE TABLE businesses AS 
SELECT * FROM '/data/businesses.csv';

-- Create traffic table
CREATE TABLE traffic AS 
SELECT * FROM '/data/traffic.csv';

-- Create indexes (DROP IF EXISTS for safety)
DROP INDEX IF EXISTS idx_residents_district;
DROP INDEX IF EXISTS idx_businesses_type;
DROP INDEX IF EXISTS idx_traffic_location;
DROP INDEX IF EXISTS idx_traffic_datetime;

CREATE INDEX idx_residents_district ON residents(district);
CREATE INDEX idx_businesses_type ON businesses(type);
CREATE INDEX idx_traffic_location ON traffic(location);
CREATE INDEX idx_traffic_datetime ON traffic(datetime);

-- Verify initialization
SELECT 'Database initialized successfully' as status;
SELECT 'residents' as table_name, COUNT(*) as row_count FROM residents
UNION ALL
SELECT 'businesses' as table_name, COUNT(*) as row_count FROM businesses  
UNION ALL
SELECT 'traffic' as table_name, COUNT(*) as row_count FROM traffic;
