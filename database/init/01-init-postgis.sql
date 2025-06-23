-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable PostGIS Topology extension for advanced spatial operations
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create a spatial reference system for Ho Chi Minh City (WGS84)
-- This is the standard coordinate system for GPS coordinates

-- Verify PostGIS installation
SELECT PostGIS_Version(); 