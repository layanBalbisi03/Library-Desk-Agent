"""
LangChain agent setup 
"""

import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import StructuredTool
from prompts import get_system_prompt
from tools import *
from models import * 

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def setup_agent():
    """Set up the LangChain agent with tools and Gemini model"""
    
    # Get API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file")
    
    print(f"API Key loaded: {google_api_key[:10]}...")
    
    # Initialize Gemini with the specified model
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  
            temperature=0.1,
            google_api_key=google_api_key
        )
        print("Using model: gemini-2.0-flash")
    except Exception as e:
        print(f"gemini-2.0-flash failed: {e}")
        # Fallback to other models
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.1,
                google_api_key=google_api_key
            )
            print("Using model: gemini-1.5-flash")
        except Exception:
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    temperature=0.1,
                    google_api_key=google_api_key
                )
                print("Using model: gemini-1.5-pro")
            except Exception:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.1,
                    google_api_key=google_api_key
                )
                print("Using model: gemini-pro")
    
    # Create tools for the agent using StructuredTool and existing models
    tools = [
        StructuredTool.from_function(
            func=find_books,
            name="find_books",
            description="Search for books by title or author",
            args_schema=FindBooksRequest
        ),
        StructuredTool.from_function(
            func=create_order,
            name="create_order",
            description="Create a new book order for a customer",
            args_schema=CreateOrderRequest
        ),
        StructuredTool.from_function(
            func=restock_book,
            name="restock_book",
            description="Add more copies of a book to inventory",
            args_schema=RestockBookRequest
        ),
        StructuredTool.from_function(
            func=update_price,
            name="update_price",
            description="Update a book's price",
            args_schema=UpdatePriceRequest
        ),
        StructuredTool.from_function(
            func=order_status,
            name="order_status",
            description="Check the status of an order",
            args_schema=OrderStatusInput
        ),
        StructuredTool.from_function(
            func=inventory_summary,
            name="inventory_summary",
            description="Get books that are running low on stock (less than 5 copies)",
            args_schema=InventorySummaryInput
        )
    ]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    
    print("AI Agent setup complete!")
    return agent_executor

# Create a global agent instance
agent_executor = setup_agent()