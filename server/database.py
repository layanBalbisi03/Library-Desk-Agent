"""
Database connection and operations 
"""

import sqlite3
import json
import os
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str = None):
        # Use absolute path to avoid relative path issues
        if db_path is None:
            # Go up one level from server/ to project root, then to db/library.db
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.db_path = os.path.join(project_root, "db", "library.db")
        else:
            self.db_path = db_path
        
        print(f"📁 Database path: {self.db_path}")  # Debug line
    
    def get_connection(self):
        """Get a fresh database connection"""
        return sqlite3.connect(self.db_path)
    
    # Book operations
    def find_books(self, query: str, search_by: str = "title") -> List[Dict]:
        """Search for books by title or author"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row  # This lets us get results as dictionaries
        cursor = conn.cursor()
        
        if search_by == "title":
            cursor.execute("SELECT * FROM books WHERE title LIKE ?", (f'%{query}%',))
        else:  # search by author
            cursor.execute("SELECT * FROM books WHERE author LIKE ?", (f'%{query}%',))
        
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    def get_book(self, isbn: str) -> Dict:
        """Get a specific book by its ISBN"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE isbn = ?", (isbn,))
        book = cursor.fetchone()
        conn.close()
        return dict(book) if book else None
    
    def update_book_stock(self, isbn: str, new_stock: int) -> bool:
        """Update a book's stock quantity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, isbn))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def update_book_price(self, isbn: str, new_price: float) -> bool:
        """Update a book's price"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET price = ? WHERE isbn = ?", (new_price, isbn))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    # Order operations
    def create_order(self, customer_id: int, items: List[Dict]) -> int:
        """Create a new order and reduce stock"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First, check if customer exists
            cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            
            # Calculate total amount and check stock
            total_amount = 0
            for item in items:
                book = self.get_book(item['isbn'])  # FIXED: isbn instead of ishn
                if not book:
                    raise ValueError(f"Book {item['isbn']} not found")
                if book['stock'] < item['qty']:
                    raise ValueError(f"Not enough stock for {book['title']}")
                total_amount += book['price'] * item['qty']
            
            # Create the order
            cursor.execute(
                "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, 'completed')",
                (customer_id, total_amount)
            )
            order_id = cursor.lastrowid
            
            # Add order items and reduce stock
            for item in items:
                book = self.get_book(item['isbn'])  # FIXED: isbn instead of ishn
                cursor.execute(
                    "INSERT INTO order_items (order_id, isbn, quantity, unit_price) VALUES (?, ?, ?, ?)",  # FIXED: isbn
                    (order_id, item['isbn'], item['qty'], book['price'])  # FIXED: isbn
                )
                # Reduce stock
                new_stock = book['stock'] - item['qty']
                cursor.execute("UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, item['isbn']))  # FIXED: isbn
            
            conn.commit()
            return order_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_order_status(self, order_id: int) -> Dict:
        """Get order details and status"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.*, c.name as customer_name 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.id 
            WHERE o.id = ?
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return None
        
        cursor.execute("""
            SELECT oi.isbn, oi.quantity, oi.unit_price, b.title 
            FROM order_items oi 
            JOIN books b ON oi.isbn = b.isbn 
            WHERE oi.order_id = ?
        """, (order_id,))
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {**dict(order), 'items': items}
    
    # Inventory operations
    def get_inventory_summary(self) -> List[Dict]:
        """Get books with low stock (less than 5 copies)"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE stock < 5 ORDER BY stock ASC")
        low_stock_books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return low_stock_books
    
    # Chat storage operations
    def save_message(self, session_id: str, role: str, content: str):
        """Save a chat message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()
    
    def save_tool_call(self, session_id: str, name: str, args: dict, result: dict):
        """Save a tool call record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tool_calls (session_id, name, args_json, result_json) VALUES (?, ?, ?, ?)",
            (session_id, name, json.dumps(args), json.dumps(result))
        )
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,)
        )
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history