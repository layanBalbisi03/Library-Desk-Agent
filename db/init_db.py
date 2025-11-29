"""
This script creates the database and fills it with sample data
"""
import sqlite3
import os

def init_database():
    # Create db directory
    os.makedirs('db', exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect('db/library.db')
    cursor = conn.cursor()
    
    print("Creating library database...")
    
    # Read and execute schema
    with open('db/schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)
    print("Database tables created!")
    
    # Read and execute seed data
    with open('db/seed.sql', 'r') as f:
        seed_data = f.read()
    cursor.executescript(seed_data)
    print("Sample data added!")
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers") 
    customer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    print(f"Database ready with:")
    print(f"   {book_count} books")
    print(f"   {customer_count} customers") 
    print(f"   {order_count} orders")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()