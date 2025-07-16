from langchain.chat_models import ChatOpenAI
from nodes.state_agent import AgentState

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0.2)


def history_node(state: AgentState) -> AgentState:
    prompt = f"""
    You are a helpful assistant that can answer questions about the conversation history.
    The task is: {state.task}
    The conversation history is: {state.conversation_history}
    The research is: {state.memory}
    and return the answer to the task based on the conversation history.
    """
    response = llm.invoke(prompt)
    updated_state = AgentState(
        task=state.task,
        memory=state.memory + [f"History: {response.content}"],
        next_action=state.next_action,
        failed_attempts=state.failed_attempts,
        decision=state.decision,
        conversation_history=state.conversation_history,
        session_id=state.session_id,
        current_state="history was checked",
    )
    return updated_state
