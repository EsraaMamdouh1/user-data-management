-- Check if the database exists, create if not
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'UserDatabase')
BEGIN
    CREATE DATABASE UserDatabase;
END;
GO

-- Use the database
USE UserDatabase;
GO

-- Check if the Users table exists, create if not
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users' AND type = 'U')
BEGIN
    CREATE TABLE Users (
        user_id VARCHAR(255) PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        age INT,
        gender VARCHAR(50),
        year_of_birth INT
    );
END;
GO
