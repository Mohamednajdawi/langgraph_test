import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from agent_builder import graph
from fastapi import FastAPI, HTTPException
from nodes.state_agent import AgentState
from pydantic import BaseModel

app = FastAPI(
    title="LangGraph Research Agent API",
    description="API for querying information using LangGraph with Wikipedia research",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    query: str
    summary: str
    research_count: int
    memory: list[str]
    status: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LangGraph Research Agent API is running"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the LangGraph research agent workflow.
    
    This endpoint:
    1. Takes a user query
    2. Plans research steps
    3. Gathers information from Wikipedia
    4. Summarizes the findings
    5. Returns the final result
    """
    try:
        initial_state = AgentState(
            task=request.query,
            memory=[],
            next_action="",
            failed_attempts=0,
            decision=""
        )
        
        with ThreadPoolExecutor() as executor:
            future = executor.submit(graph.invoke, initial_state)
            final_state = await asyncio.get_event_loop().run_in_executor(None, future.result)
        
        summary = ""
        for entry in final_state["memory"]:
            if entry.startswith("Final Summary:"):
                summary = entry.replace("Final Summary: ", "")
                break
        
        research_entries = [entry for entry in final_state["memory"] if entry.startswith("Researcher found:")]
        
        return QueryResponse(
            query=request.query,
            summary=summary,
            research_count=len(research_entries),
            memory=final_state["memory"],
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check with component status"""
    import os
    try:
        test_state = AgentState(
            task="test",
            memory=[],
            next_action="",
            failed_attempts=0,
            decision=""
        )
        
        return {
            "status": "healthy",
            "components": {
                "fastapi": "running",
                "langgraph": "available",
                "openai": "configured" if "OPENAI_API_KEY" in os.environ else "not configured",
                "wikipedia": "available"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import os

    import uvicorn

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
    
    print("🚀 Starting LangGraph Research Agent API...")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
