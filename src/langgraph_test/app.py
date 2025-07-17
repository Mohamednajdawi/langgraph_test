import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent_builder import graph
from fastapi import FastAPI, HTTPException
from nodes.state_agent import AgentState, ConversationEntry
from pydantic import BaseModel

app = FastAPI(
    title="LangGraph Research Agent API",
    description="API for querying information using LangGraph with Wikipedia research",
    version="1.0.0",
)

# In-memory session storage (you can replace with database later)
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    summary: str
    research_count: int
    memory: list[str]
    status: str
    session_id: str
    conversation_history: List[ConversationEntry] = []


def load_conversation_history(session_id: str) -> List[ConversationEntry]:
    """Load conversation history from file"""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if session_file.exists():
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
                return [ConversationEntry(**entry) for entry in data]
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
    return []


def save_conversation_history(session_id: str, history: List[ConversationEntry]):
    """Save conversation history to file"""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    try:
        with open(session_file, "w") as f:
            json.dump([entry.dict() for entry in history], f, indent=2)
    except Exception as e:
        print(f"Error saving session {session_id}: {e}")


def generate_session_id() -> str:
    """Generate a new session ID"""
    import uuid

    return str(uuid.uuid4())


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LangGraph Research Agent API is running"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the LangGraph research agent workflow.

    This endpoint:
    1. Takes a user query (with optional session_id)
    2. Loads conversation history if session exists
    3. Plans research steps with conversation context
    4. Gathers information from Wikipedia
    5. Summarizes the findings
    6. Saves conversation history
    7. Returns the final result
    """
    try:
        # Handle session management
        session_id = request.session_id or generate_session_id()
        conversation_history = load_conversation_history(session_id)

        initial_state = AgentState(
            task=request.query,
            memory=[],
            next_action="",
            failed_attempts=0,
            decision="",
            conversation_history=conversation_history,
            session_id=session_id,
        )

        with ThreadPoolExecutor() as executor:
            future = executor.submit(graph.invoke, initial_state)
            final_state = await asyncio.get_event_loop().run_in_executor(
                None, future.result
            )

        summary = ""
        for entry in final_state["memory"]:
            if entry.startswith("Final Summary:"):
                summary = entry.replace("Final Summary: ", "")
                break

        research_entries = [
            entry
            for entry in final_state["memory"]
            if entry.startswith("Researcher found:")
        ]

        # Add this conversation to history
        new_entry = ConversationEntry(
            query=request.query, summary=summary, timestamp=datetime.now().isoformat()
        )
        conversation_history.append(new_entry)
        save_conversation_history(session_id, conversation_history)

        return QueryResponse(
            query=request.query,
            summary=summary,
            research_count=len(research_entries),
            memory=final_state["memory"],
            status="completed",
            session_id=session_id,
            conversation_history=conversation_history,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a specific session"""
    try:
        history = load_conversation_history(session_id)
        return {
            "session_id": session_id,
            "conversation_count": len(history),
            "history": history,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving history: {str(e)}"
        )


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a specific session"""
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")


@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = []
        for session_file in SESSIONS_DIR.glob("*.json"):
            session_id = session_file.stem
            history = load_conversation_history(session_id)
            if history:
                sessions.append(
                    {
                        "session_id": session_id,
                        "conversation_count": len(history),
                        "last_query": history[-1].query if history else None,
                        "last_timestamp": history[-1].timestamp if history else None,
                    }
                )
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check with component status"""
    try:
        test_state = AgentState(
            task="test",
            memory=[],
            next_action="",
            failed_attempts=0,
            decision="",
            conversation_history=[],
            session_id="test",
        )

        return {
            "status": "healthy",
            "components": {
                "fastapi": "running",
                "langgraph": "available",
                "openai": "configured"
                if "OPENAI_API_KEY" in os.environ
                else "not configured",
                "wikipedia": "available",
                "sessions": "enabled",
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")

    print("🚀 Starting LangGraph Research Agent API...")
    print("📖 API Documentation available at: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
