import re

from langchain.chat_models import ChatOpenAI
from nodes.state_agent import AgentState
from nodes.stopper_node import make_decision

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0.2)

def trim_quoted_text(s):
    match = re.search(r'\[(.*?)\]', s)
    return match.group(1) if match else s

def planner_node(state: AgentState) -> AgentState:
    research_entries = [entry for entry in state.memory if entry.startswith("Researcher found:")]
    
    # Build conversation context
    conversation_context = ""
    if state.conversation_history:
        conversation_context = "\nCONVERSATION HISTORY:\n"
        for i, entry in enumerate(state.conversation_history[-3:], 1):  # Show last 3 conversations
            conversation_context += f"{i}. Q: {entry.query}\n   A: {entry.summary[:100]}{'...' if len(entry.summary) > 100 else ''}\n"
        conversation_context += "\nUse this context to understand follow-up questions or related queries.\n\n"
    
    prompt = (
        f"You are planning how to complete this task: '{state.task}'\n\n"
        
        f"{conversation_context}"
        
        f"Current research gathered:\n{state.memory}\n\n"
        
        f"Research status: {len(research_entries)} pieces of information collected.\n\n"
        
        "STOPPING CONDITIONS:\n"
        "Reply with exactly 'STOP' if ANY of these conditions are met:\n"
        "- You have gathered 3 or more pieces of research information\n"
        "- The existing information sufficiently covers the basic concepts needed for the task\n"
        "- You have enough information to complete the task\n"
        "- The question can be answered from conversation history (avoid duplicate research)\n\n"
        
        "TASK BREAKDOWN:\n"
        "If the task contains multiple questions or components:\n"
        "- Break it down into smaller, focused subtasks\n"
        "- Handle one subtask at a time\n"
        "- Example: 'What is the capital of France and what language is spoken in Jordan?'\n"
        "  → First research: 'capital France'\n"
        "  → Second research: 'language Jordan'\n\n"
        "Always check the Current research "
        "SEARCH INSTRUCTIONS:\n"
        "If you need more information, provide ONE concise search term (1-3 words).\n"
        "Examples: 'photosynthesis', 'Leo Messi', 'American Shorthair'\n\n"
        "the search term should be inside a brackets:  [search term] "
        "All questions should be answered before you stop"
        "Focus on what specific information is missing and provide the most relevant search term."
        "if the task is about something in the conversation history, you should reply with 'check_history'"
    )

    response = llm.invoke(prompt)
    trim_research_term = trim_quoted_text(response.content)
    print(f"Planner response: {trim_research_term}")
    
    # Decision logic - determine next step
    decision = make_decision(state, trim_research_term)
    
    updated_state = AgentState(
        task=state.task,
        memory=state.memory + [f"Planner: {trim_research_term}"],
        next_action=trim_research_term,
        failed_attempts=state.failed_attempts,
        decision=decision,
        conversation_history=state.conversation_history,
        session_id=state.session_id
    )
    print(f"Planner decision: {decision}")

    return updated_state
