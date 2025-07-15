from langchain_community.chat_models import ChatOpenAI

from .state_agent import AgentState

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)

def summarizer_node(state: AgentState) -> AgentState:
    research_entries = [entry for entry in state.memory if entry.startswith("Researcher found:")]
    research_data = "\n\n".join([entry.replace("Researcher found: ", "") for entry in research_entries])
    
    prompt = (
        f"Based on the research gathered, provide a concise and clear answer to: '{state.task}'\n\n"
        f"Research data:\n{research_data}\n\n"
        "Please synthesize this information into a comprehensive but concise answer. "
        "Focus on the key concepts and processes. Keep it under 200 words."
    )
    
    response = llm.invoke(prompt)
    summary = response.content
    
    state.next_action = "COMPLETED"
    state.memory = state.memory + [f"Final Summary: {summary}"]
    return state