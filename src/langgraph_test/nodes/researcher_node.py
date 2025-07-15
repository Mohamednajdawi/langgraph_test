from tools.wiki_tool import wiki_search

from .state_agent import AgentState


def researcher_node(state: AgentState) -> AgentState:
    print(f"Researcher: {state.next_action}")
    search_term = state.next_action.strip()
    result = wiki_search(search_term)
    if "No relevant result" in result:
        state.failed_attempts += 1
    else:
        state.failed_attempts = 0

    state.memory = state.memory + [f"Researcher found: {result}"]
    state.failed_attempts = state.failed_attempts
    return state