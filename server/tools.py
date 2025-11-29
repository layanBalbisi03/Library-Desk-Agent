"""
Agent Tools - FIXED TO HANDLE PYDANTIC MODELS
"""

from typing import Dict, Any, List
from database import Database
from models import *

db = Database()

def find_books(**kwargs) -> List[Dict]:
    """
    Search for books by title or author
    
    Args:
        **kwargs: Keyword arguments with 'q' (search query) and 'by' (search type)
    
    Returns:
        List of matching books
    """
    # Extract values from Pydantic model or dict
    if hasattr(kwargs.get('q', ''), 'q'):
        # It's a Pydantic model, extract the field
        query = kwargs['q'].q
        search_by = kwargs['q'].by
    else:
        # It's a regular dict
        query = kwargs.get('q', '')
        search_by = kwargs.get('by', 'title')
    
    books = db.find_books(query, search_by)
    return books

def create_order(**kwargs) -> Dict[str, Any]:
    """
    Create a new order for a customer
    
    Args:
        **kwargs: Keyword arguments with 'customer_id' and 'items' (list of book items)
    
    Returns:
        Order details and updated stock info
    """
    # Extract values from Pydantic model or dict
    if hasattr(kwargs.get('customer_id', ''), 'customer_id'):
        # It's a Pydantic model
        customer_id = kwargs['customer_id'].customer_id
        items = kwargs['customer_id'].items
    else:
        # It's a regular dict
        customer_id = kwargs.get('customer_id')
        items = kwargs.get('items', [])
    
    # Convert items to the format expected by database
    db_items = []
    for item in items:
        if hasattr(item, 'isbn'):
            # It's a Pydantic OrderItem model
            db_items.append({'isbn': item.isbn, 'qty': item.qty})
        else:
            # It's a regular dict
            db_items.append({'isbn': item['isbn'], 'qty': item['qty']})
    
    order_id = db.create_order(customer_id, db_items)
    
    # Get the created order details
    order = db.get_order_status(order_id)
    
    # Get updated stock for ordered books
    stock_updates = []
    for item in db_items:
        book = db.get_book(item['isbn'])
        if book:
            stock_updates.append({
                'title': book['title'],
                'new_stock': book['stock']
            })
    
    return {
        'order_id': order_id,
        'customer': order['customer_name'],
        'total_amount': order['total_amount'],
        'stock_updates': stock_updates
    }

def restock_book(**kwargs) -> Dict[str, Any]:
    """
    Add more copies of a book to inventory
    
    Args:
        **kwargs: Keyword arguments with 'isbn' and 'qty'
    
    Returns:
        Updated book information
    """
    # Extract values from Pydantic model or dict
    if hasattr(kwargs.get('isbn', ''), 'isbn'):
        # It's a Pydantic model
        isbn = kwargs['isbn'].isbn
        qty = kwargs['isbn'].qty
    else:
        # It's a regular dict
        isbn = kwargs.get('isbn')
        qty = kwargs.get('qty')
    
    book = db.get_book(isbn)
    if not book:
        return {"error": f"Book with ISBN {isbn} not found"}
    
    new_stock = book['stock'] + qty
    success = db.update_book_stock(isbn, new_stock)
    
    if success:
        updated_book = db.get_book(isbn)
        return {
            'title': updated_book['title'],
            'new_stock': updated_book['stock'],
            'message': f"Restocked {qty} copies of {updated_book['title']}"
        }
    else:
        return {"error": "Failed to restock book"}

def update_price(**kwargs) -> Dict[str, Any]:
    """
    Update the price of a book
    
    Args:
        **kwargs: Keyword arguments with 'isbn' and 'price'
    
    Returns:
        Updated book information
    """
    # Extract values from Pydantic model or dict
    if hasattr(kwargs.get('isbn', ''), 'isbn'):
        # It's a Pydantic model
        isbn = kwargs['isbn'].isbn
        price = kwargs['isbn'].price
    else:
        # It's a regular dict
        isbn = kwargs.get('isbn')
        price = kwargs.get('price')
    
    book = db.get_book(isbn)
    if not book:
        return {"error": f"Book with ISBN {isbn} not found"}
    
    success = db.update_book_price(isbn, price)
    
    if success:
        updated_book = db.get_book(isbn)
        return {
            'title': updated_book['title'],
            'new_price': updated_book['price'],
            'message': f"Updated price of {updated_book['title']} to ${price}"
        }
    else:
        return {"error": "Failed to update price"}

def order_status(**kwargs) -> Dict[str, Any]:
    """
    Check the status of an order
    
    Args:
        **kwargs: Keyword arguments with 'order_id'
    
    Returns:
        Order details and items
    """
    # Extract values from Pydantic model or dict
    if hasattr(kwargs.get('order_id', ''), 'order_id'):
        # It's a Pydantic model
        order_id = kwargs['order_id'].order_id
    else:
        # It's a regular dict
        order_id = kwargs.get('order_id')
    
    order = db.get_order_status(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    return order

def inventory_summary(**kwargs) -> Dict[str, Any]:
    """
    Get books that are running low on stock
    
    Args:
        **kwargs: Keyword arguments (not used)
    
    Returns:
        List of books with low stock
    """
    low_stock_books = db.get_inventory_summary()
    return {
        'low_stock_books': low_stock_books,
        'count': len(low_stock_books)
    }