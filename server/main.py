"""
FastAPI Server - The main application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os

# Import components
from database import Database
from agent import agent_executor
from models import *

app = FastAPI(title="Library Desk Agent", version="1.0.0")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

# Serve frontend files
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
app_dir = os.path.join(project_root, "app")

# Mount static files if app directory exists
if os.path.exists(app_dir):
    app.mount("/app", StaticFiles(directory=app_dir, html=True), name="app")
    print(f"📁 Serving frontend from: {app_dir}")
else:
    print(f"⚠️  Frontend directory not found: {app_dir}")

# Chat request model
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str] = []

@app.get("/")
async def root():
    return {"message": "Library Desk Agent API is running! Go to /app/ for the chat interface."}

# Redirect root to app if requested
@app.get("/app/")
async def serve_frontend():
    index_path = os.path.join(app_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "Frontend not found. Please check if the app folder exists."}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - talk to the AI librarian"""
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Get chat history for context
        history = db.get_chat_history(session_id)
        
        # Prepare conversation history for the agent
        chat_history = []
        for msg in history:
            if msg['role'] == 'user':
                chat_history.append(("human", msg['content']))
            else:
                chat_history.append(("ai", msg['content']))
        
        # Save user message
        db.save_message(session_id, "user", request.message)
        
        # Invoke the agent
        result = agent_executor.invoke({
            "input": request.message,
            "chat_history": chat_history
        })
        
        response_text = result.get("output", "I apologize, but I couldn't process your request.")
        
        # Save AI response
        db.save_message(session_id, "assistant", response_text)
        
        # Track which tools were used (for response)
        tools_used = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                tool_name = step[0].tool
                tools_used.append(tool_name)
                
                # Save tool call to database
                db.save_tool_call(
                    session_id=session_id,
                    name=tool_name,
                    args=step[0].tool_input,
                    result=step[1]
                )
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            tools_used=tools_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Tool endpoints 
@app.post("/tools/find_books")
async def api_find_books(request: FindBooksRequest):
    """Direct endpoint to search books"""
    books = db.find_books(request.q, request.by)
    return {"books": books}

@app.post("/tools/create_order")
async def api_create_order(request: CreateOrderRequest):
    """Direct endpoint to create orders"""
    try:
        # Convert to the format expected by the tool
        items_dict = [{"isbn": item.isbn, "qty": item.qty} for item in request.items]
        result = create_order({"customer_id": request.customer_id, "items": items_dict})
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tools/order_status/{order_id}")
async def api_order_status(order_id: int):
    """Direct endpoint to check order status"""
    result = order_status({"order_id": order_id})
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/tools/inventory_summary")
async def api_inventory_summary():
    """Direct endpoint to get low stock books"""
    result = inventory_summary()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)