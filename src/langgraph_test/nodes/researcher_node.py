from tools.wiki_tool import wiki_search

from .state_agent import AgentState


def researcher_node(state: AgentState) -> AgentState:
    search_term = state.next_action.strip()
    result = wiki_search(search_term)
    # print(f"Researcher result: {result}")
    if "No relevant result" in result:
        state.failed_attempts += 1
        state.current_state = "researcher failed, change the search term"
    else:
        state.failed_attempts = 0
        state.current_state = "researcher succeeded"

    state.memory = state.memory + [f"Researcher found: {result}"]
    state.failed_attempts = state.failed_attempts
    state.current_state = "researcher succeeded"
    return state
