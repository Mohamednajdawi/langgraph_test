from langchain.chat_models import ChatOpenAI

from .state_agent import AgentState

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)


def summarizer_node(state: AgentState) -> AgentState:
    research_entries = [
        entry for entry in state.memory if entry.startswith("Researcher found:")
    ]
    research_data = "\n\n".join(
        [entry.replace("Researcher found: ", "") for entry in research_entries]
    )

    # Add conversation context if available
    conversation_context = ""
    if state.conversation_history:
        conversation_context = "\n\nCONVERSATION CONTEXT:\n"
        for entry in state.conversation_history[
            -2:
        ]:  # Last 2 conversations for context
            conversation_context += (
                f"Previous Q: {entry.query}\nPrevious A: {entry.summary}\n\n"
            )
        conversation_context += "Use this context to provide a more coherent answer that builds on previous discussions.\n"

    prompt = (
        f"Based on the research gathered, provide a concise and clear answer to: '{state.task}'\n\n"
        f"Research data:\n{research_data}\n\n"
        f"{conversation_context}"
        "Please synthesize this information into a comprehensive but concise answer. "
        "Focus on the key concepts and processes. Keep it under 200 words. "
        "Do not include any information that was not found in the research. "
        "If this is a follow-up question, acknowledge the connection to previous discussions."
    )

    response = llm.invoke(prompt)
    summary = response.content

    state.next_action = "COMPLETED"
    state.memory = state.memory + [f"Final Summary: {summary}"]
    state.current_state = "summarizer was done"
    return state
