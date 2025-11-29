-- This file creates all the tables needed for the library system

-- Books table
CREATE TABLE IF NOT EXISTS books (
    isbn TEXT PRIMARY KEY,           
    title TEXT NOT NULL,            
    author TEXT NOT NULL,          
    price DECIMAL(10,2) DEFAULT 0,   
    stock INTEGER DEFAULT 0,         
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              
    email TEXT UNIQUE,               
    phone TEXT,                     
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table 
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,   
    status TEXT DEFAULT 'pending',   
    total_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Order items 
CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL,       
    isbn TEXT NOT NULL,              
    quantity INTEGER NOT NULL,      
    unit_price DECIMAL(10,2) NOT NULL, 
    PRIMARY KEY (order_id, isbn),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (isbn) REFERENCES books(isbn)
);

-- Chat messages 
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,        
    role TEXT NOT NULL,              
    content TEXT NOT NULL,         
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool calls 
CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,        
    name TEXT NOT NULL,             
    args_json TEXT NOT NULL,         
    result_json TEXT NOT NULL,       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);