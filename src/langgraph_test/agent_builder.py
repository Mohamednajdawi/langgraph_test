from langgraph.graph import END, StateGraph
from nodes import (
    AgentState,
    examiner_decision,
    examiner_node,
    history_node,
    planner_decision,
    planner_node,
    researcher_node,
    summarizer_node,
)

builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("research", researcher_node)
builder.add_node("summarize", summarizer_node)
builder.add_node("examiner", examiner_node)
builder.add_node("history", history_node)

builder.set_entry_point("planner")
builder.add_conditional_edges(
    "planner",
    planner_decision,
    {"research": "research", "summarize": "summarize", "history": "history"},
)

builder.add_edge("research", "planner")
builder.add_edge("summarize", "examiner")
builder.add_edge("history", "planner")
builder.add_conditional_edges(
    "examiner", examiner_decision, {"planner": "planner", "correct": END}
)

graph = builder.compile()
