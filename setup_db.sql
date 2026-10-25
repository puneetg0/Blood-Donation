-- Run this once as the postgres superuser to create the app user and database.
-- In a terminal: psql -U postgres -f setup_db.sql

-- 1. Create the application user (choose your own password)
CREATE USER bdm_user WITH LOGIN;
\password bdm_user

-- 2. Create the database owned by that user
CREATE DATABASE blood_donation OWNER bdm_user;

-- 3. Grant all privileges (belt-and-suspenders)
GRANT ALL PRIVILEGES ON DATABASE blood_donation TO bdm_user;
