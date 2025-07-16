from typing import List, Optional

from pydantic import BaseModel


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
    current_state: str = "just started"
