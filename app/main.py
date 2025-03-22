from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from agent import create_agent, AgentState
import uuid

# Load environment variables
load_dotenv()

app = FastAPI(title="Python Mentor Agent")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store active sessions
sessions = {}

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def get_home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Process a chat message"""
    try:
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Get or create agent state with new structure
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "next_step": "route",
                "context": {}
            }
        
        state = sessions[session_id]
        
        # Add user message to state
        state["messages"].append({"role": "user", "content": chat_message.message})
        
        # Run agent
        agent = create_agent()
        new_state = agent.invoke(state)
        
        # Update session state
        sessions[session_id] = new_state
        
        # Get assistant response
        assistant_messages = [m for m in new_state["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "I didn't understand that."
        
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        print(f"Error processing chat: {e}")
        # Return a friendly error message
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request. Please try again with a different question.",
            session_id=chat_message.session_id or str(uuid.uuid4())
        )

@app.get("/sessions")
async def get_sessions():
    """Get active sessions (for debugging)"""
    return {"session_count": len(sessions), "session_ids": list(sessions.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)