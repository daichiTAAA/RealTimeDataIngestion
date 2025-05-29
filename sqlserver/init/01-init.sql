-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'testdb')
BEGIN
    CREATE DATABASE testdb;
END
GO

USE testdb;
GO

-- Enable CDC on the database
EXEC sys.sp_cdc_enable_db;
GO

-- Create a sample users table
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
GO

-- Create a sample products table
CREATE TABLE products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description NTEXT,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
GO

-- Enable CDC for the users table
EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = N'users',
    @role_name = NULL,
    @capture_instance = NULL,
    @supports_net_changes = 1;
GO

-- Enable CDC for the products table
EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = N'products',
    @role_name = NULL,
    @capture_instance = NULL,
    @supports_net_changes = 1;
GO

-- Insert some sample data
INSERT INTO users (name, email) VALUES 
    ('John Doe SQL', 'john.sql@example.com'),
    ('Jane Smith SQL', 'jane.sql@example.com'),
    ('Bob Johnson SQL', 'bob.sql@example.com');
GO

INSERT INTO products (name, price, description) VALUES 
    ('SQL Laptop', 1099.99, 'High-performance laptop for SQL Server'),
    ('SQL Mouse', 39.99, 'Wireless optical mouse for SQL Server'),
    ('SQL Keyboard', 89.99, 'Mechanical keyboard for SQL Server');
GO

-- Create trigger for updating updated_at timestamp on users table
CREATE TRIGGER tr_users_updated_at
ON users
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE users
    SET updated_at = GETDATE()
    FROM users u
    INNER JOIN inserted i ON u.id = i.id;
END
GO

-- Create trigger for updating updated_at timestamp on products table
CREATE TRIGGER tr_products_updated_at
ON products
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE products
    SET updated_at = GETDATE()
    FROM products p
    INNER JOIN inserted i ON p.id = i.id;
END
GO