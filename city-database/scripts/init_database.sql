-- Initialize City Database with MCP Support
-- This script loads CSV data into DuckDB tables

-- Create residents table
CREATE TABLE residents AS 
SELECT * FROM '/data/residents.csv';

-- Create businesses table  
CREATE TABLE businesses AS 
SELECT * FROM '/data/businesses.csv';

-- Create traffic table
CREATE TABLE traffic AS 
SELECT * FROM '/data/traffic.csv';

-- Create indexes for better performance
CREATE INDEX idx_residents_district ON residents(district);
CREATE INDEX idx_businesses_type ON businesses(type);
CREATE INDEX idx_traffic_location ON traffic(location);
CREATE INDEX idx_traffic_datetime ON traffic(datetime);

-- Show table information
SELECT 'Database initialized successfully' as status;
SELECT 'residents' as table_name, COUNT(*) as row_count FROM residents
UNION ALL
SELECT 'businesses' as table_name, COUNT(*) as row_count FROM businesses  
UNION ALL
SELECT 'traffic' as table_name, COUNT(*) as row_count FROM traffic;
