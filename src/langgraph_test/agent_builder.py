from langgraph.graph import END, StateGraph
from nodes.examiner_node import examiner_node
from nodes.history_node import history_node
from nodes.planner_node import planner_node
from nodes.researcher_node import researcher_node
from nodes.state_agent import AgentState
from nodes.stopper_node import examiner_decision, planner_decision
from nodes.summarizer_node import summarizer_node

builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("research", researcher_node)
builder.add_node("summarize", summarizer_node)
builder.add_node("examiner", examiner_node)
builder.add_node("history", history_node)

builder.set_entry_point("planner")
builder.add_conditional_edges("planner", planner_decision, {
    "research": "research",
    "summarize": "summarize",
    "history": "history"
})

builder.add_edge("research", "planner")
builder.add_edge("summarize", "examiner")
builder.add_edge("history", "planner")
builder.add_conditional_edges("examiner", examiner_decision, {
    "planner": "planner",
    "correct": END
})

graph = builder.compile()