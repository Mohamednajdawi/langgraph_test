from nodes.state_agent import AgentState


def make_decision(state: AgentState, planner_response: str) -> str:
    """Decide whether to go to research or summarize based on current state and planner response"""
    
    # Check if planner explicitly said to stop
    if "stop" in planner_response.lower():
        print("🛑 Planner decided to stop - Moving to summarizer...")
        return "summarize"
    
    research_entries = [entry for entry in state.memory if entry.startswith("Researcher found:")]
    
    # Auto-stop conditions
    if len(research_entries) >= 3 or len(state.memory) > 12 or state.failed_attempts >= 3:
        print("🛑 Auto-stopping: Gathered sufficient information (3+ research results) or maximum iterations reached or too many failed attempts")
        return "summarize"
    
    print("📚 Continuing research...")
    return "research"

def planner_decision(state: AgentState) -> str:
    """Decision function for conditional edges"""
    return state.decision