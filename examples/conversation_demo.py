#!/usr/bin/env python3
"""
Example script demonstrating conversation history with the LangGraph Research Agent
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def query_agent(query: str, session_id: str = None):
    """Send a query to the agent"""
    payload = {"query": query}
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    return response.json()

def get_history(session_id: str):
    """Get conversation history for a session"""
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/history")
    return response.json()

def list_sessions():
    """List all active sessions"""
    response = requests.get(f"{BASE_URL}/sessions")
    return response.json()

def main():
    print("🤖 LangGraph Research Agent - Conversation History Demo\n")
    
    # First query - this will create a new session
    print("1. First query (creates new session):")
    result1 = query_agent("What is photosynthesis?")
    session_id = result1["session_id"]
    print(f"   Session ID: {session_id}")
    print(f"   Answer: {result1['summary'][:100]}...")
    print()
    
    # Second query - related follow-up using same session
    print("2. Follow-up query (same session):")
    result2 = query_agent("How does it work in plants?", session_id)
    print(f"   Answer: {result2['summary'][:100]}...")
    print()
    
    # Third query - another follow-up
    print("3. Another follow-up (same session):")
    result3 = query_agent("What are the products of this process?", session_id)
    print(f"   Answer: {result3['summary'][:100]}...")
    print()
    
    # Show conversation history
    print("4. Conversation history:")
    history = get_history(session_id)
    for i, entry in enumerate(history["history"], 1):
        print(f"   {i}. Q: {entry['query']}")
        print(f"      A: {entry['summary'][:80]}...")
        print(f"      Time: {entry['timestamp']}")
        print()
    
    # List all sessions
    print("5. All active sessions:")
    sessions = list_sessions()
    for session in sessions["sessions"]:
        print(f"   Session: {session['session_id'][:8]}...")
        print(f"   Conversations: {session['conversation_count']}")
        print(f"   Last query: {session['last_query']}")
        print()

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running with: python src/langgraph_test/app.py")
    except Exception as e:
        print(f"❌ Error: {e}") 