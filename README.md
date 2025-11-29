#  Library AI Agent

This project is a small full-stack system that simulates a **library help desk AI agent**.  
The agent chats with users and can **search books, create orders, update stock, check inventory, and more** using real database operations.

It uses:
- **SQLite** for data  
- **FastAPI** for backend  
- **LangChain** for AI agent + tools  
- **Gemini API** as the LLM  
- **HTML/CSS/JS** as a simple frontend  


#  Database (db/)

### **schema.sql**
Defines all tables used in the library system:
- `books`
- `customers`
- `orders`
- `order_items`
- `messages` 
- `tool_calls` 

Includes **primary keys**, **foreign keys**, and table relationships.

### **seed.sql**
Inserts sample books, customers, and order data.

### **init.py**
Creates the database folder and:
1. Builds tables from `schema.sql`
2. Inserts sample data from `seed.sql`
3. Prints table counts  


#  Backend (server/)

## **database.py**
Contains all database operations:
- Search books  
- Get book details  
- Update price  
- Update stock  
- Create orders  
- Write order items  
- Check order status  
- Save chat messages  
- Save tool calls  

This file isolates the DB layer to keep the system modular.

## **models.py**
Defines **Pydantic models** that shape and validate input/output data.

Examples:
- `FindBooksRequest`
- `CreateOrderRequest`
- `OrderItem`
- `RestockBookRequest`
- `OrderStatusResponse`

Pydantic ensures the agent receives structured and correct data.

## **tools.py**
Defines all **actions the AI agent can perform**, such as:
- `find_books`
- `create_order`
- `restock_book`
- `update_price`
- `order_status`
- `inventory_summary`

These tools:
- Use the database functions  
- Return clean JSON-friendly dictionaries  

LangChain calls these tools when needed.

## **agent.py**
Sets up the **LangChain agent** with:
- Gemini LLM  
- Structured tools  
- System prompt  
- Chat memory handling  
- Tool routing  

Steps performed:
1. Load Gemini API key  
2. Initialize Gemini model  
3. Wrap Python functions as LangChain `StructuredTool`s  
4. Build a prompt template  
5. Create a tool-aware agent  
6. Create the `AgentExecutor`  

This enables the LLM to **decide when to use a tool**, pass validated data to it, and return results.

## **main.py**
FastAPI backend that:
- Defines `/chat` endpoint for messages
- Sends user messages to the agent
- Returns agent responses
- Exposes `/history` to load past messages  
- Acts as the bridge between frontend and agent  

#  Frontend (app/)

A simple web UI:
- **index.html** : Chat interface  
- **style.css** : Simple layout and theme  
- **script.js** : Sends requests to FastAPI, displays responses  

#  Running the Project

### 1️-Install dependencies
pip install -r requirements.txt

### 2️-Set up environment variables
Copy `.env.example` → `.env` and add:
GOOGLE_API_KEY=your_api_key_here

### 3️-Build the database
cd db
python init.py

### 4️-Start backend server
cd server
python main.py

### 5️-Open the UI  
Open `app/index.html` in your browser.

#  Example Outputs

## Create Order
- user: We sold 3 copies of Clean Code to customer 2 today. Create the order.
- agent: OK. I've created order #11 for customer 2. The stock of Clean Code has been updated. There is now 1 copy left. The total amount is $150.

## Search Books
- user: list the books by Eric Matthes
- agent: I found one book by Eric Matthes: Python Crash Course. It is in stock with 20 copies and costs $29.99.

## Restock Book
- user: Restock The Pragmatic Programmer book 978-0135957059 by 10
- agent: OK. I've restocked 'The Pragmatic Programmer'. New stock: 18 copies.

## Order Status
- user: show me the status of order 10
- agent: Order #10 status: Completed, Total: $92.99, Books: Clean Code, Effective Java