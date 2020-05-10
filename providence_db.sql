-- Database: providencedb

-- DROP DATABASE providencedb;

CREATE DATABASE providencedb
    WITH 
    OWNER = providence
    ENCODING = 'UTF8'
    LC_COLLATE = 'fr_FR.UTF-8'
    LC_CTYPE = 'fr_FR.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE providencedb
    IS 'Base de données application Providence';