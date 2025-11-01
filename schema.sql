-- ============================================
-- Order Management System - Database Schema
-- ============================================

-- Create database (run this separately)
-- CREATE DATABASE order_management;

-- Connect to database
-- \c order_management

-- ============================================
-- Drop existing tables (for clean setup)
-- ============================================
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- Users Table
-- Stores user authentication and profile data
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create index on email for faster login queries
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- Orders Table
-- Stores order information and status
-- ============================================
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    -- Check constraints
    CONSTRAINT orders_amount_check CHECK (amount > 0),
    CONSTRAINT orders_status_check CHECK (status IN ('pending', 'processing', 'completed', 'cancelled'))
);

-- Create indexes for faster queries
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- Composite index for common query pattern
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- ============================================
-- Trigger to auto-update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Sample Data (Optional - for testing)
-- ============================================

-- Insert sample user (password: testpass123)
INSERT INTO users (name, email, password_hash) VALUES
('Test User', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lSQOxKvfvqJu');

-- Insert sample orders
INSERT INTO orders (user_id, product_name, amount, status) VALUES
(1, 'Laptop', 999.99, 'pending'),
(1, 'Mouse', 29.99, 'completed'),
(1, 'Keyboard', 79.99, 'pending');

-- ============================================
-- Useful Queries
-- ============================================

-- Get all pending orders
-- SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC;

-- Get user's order history
-- SELECT o.*, u.name as user_name 
-- FROM orders o 
-- JOIN users u ON o.user_id = u.id 
-- WHERE u.email = 'test@example.com';

-- Get order statistics by status
-- SELECT status, COUNT(*) as count, SUM(amount) as total_amount 
-- FROM orders 
-- GROUP BY status;

-- ============================================
-- Cleanup Queries (if needed)
-- ============================================

-- Delete all orders
-- DELETE FROM orders;

-- Delete all users (will cascade delete orders)
-- DELETE FROM users;

-- Reset sequences
-- ALTER SEQUENCE users_id_seq RESTART WITH 1;
-- ALTER SEQUENCE orders_id_seq RESTART WITH 1;