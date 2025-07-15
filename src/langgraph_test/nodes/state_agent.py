
from pydantic import BaseModel


class AgentState(BaseModel):
    task: str
    memory: list[str]
    next_action: str
    failed_attempts: int
    decision: str

