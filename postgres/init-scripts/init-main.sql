-- Create admin user if not exists
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pgadmin') THEN
    CREATE ROLE pgadmin WITH LOGIN PASSWORD 'admin123' SUPERUSER;
  END IF;
  
  -- Create application user
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'chatuser') THEN
    CREATE ROLE chatuser WITH LOGIN PASSWORD 'avijit123' CREATEDB;
  END IF;
END $$;

-- Create databases
CREATE DATABASE auth_service_db OWNER chatuser;
CREATE DATABASE user_service_db OWNER chatuser;
CREATE DATABASE chat_service_db OWNER chatuser;

-- Set permissions
\c auth_service_db
GRANT ALL ON SCHEMA public TO chatuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chatuser;

\c user_service_db
GRANT ALL ON SCHEMA public TO chatuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chatuser;

\c chat_service_db
GRANT ALL ON SCHEMA public TO chatuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chatuser;