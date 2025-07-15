
from pydantic import BaseModel
from typing import List, Dict, Optional


class ConversationEntry(BaseModel):
    query: str
    summary: str
    timestamp: str


class AgentState(BaseModel):
    task: str
    memory: list[str]
    next_action: str
    failed_attempts: int
    decision: str
    conversation_history: List[ConversationEntry] = []
    session_id: Optional[str] = None

