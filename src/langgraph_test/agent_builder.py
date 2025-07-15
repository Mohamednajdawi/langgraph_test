from langgraph.graph import END, StateGraph
from nodes.planner_node import planner_node
from nodes.researcher_node import researcher_node
from nodes.state_agent import AgentState
from nodes.stopper_node import planner_decision
from nodes.summarizer_node import summarizer_node

builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("research", researcher_node)
builder.add_node("summarize", summarizer_node)

builder.set_entry_point("planner")
builder.add_conditional_edges("planner", planner_decision, {
    "research": "research",
    "summarize": "summarize"
})
builder.add_edge("research", "planner")
builder.add_edge("summarize", END)

graph = builder.compile()