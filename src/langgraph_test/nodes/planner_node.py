from langchain.chat_models import ChatOpenAI
from nodes.state_agent import AgentState
from nodes.stopper_node import make_decision

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)

def planner_node(state: AgentState) -> AgentState:
    research_entries = [entry for entry in state.memory if entry.startswith("Researcher found:")]
    
    prompt = (
        f"You are planning how to complete this task: '{state.task}'.\n"
        f"Here is what you've gathered so far:\n{state.memory}\n\n"
        f"You have gathered {len(research_entries)} pieces of information.\n\n"
        "IMPORTANT: If you have gathered 3 or more pieces of research information, "
        "or if the information already covers the basic concepts of the task "
        "reply with exactly: 'STOP'\n\n"
        "If you need more specific information, provide a SHORT search term (1-3 words). "
        "Examples: 'photosynthesis', 'Leo Messi', 'shakira', 'american shorthair'"
        "Assest the task and only use research task if you need more information"
        "If 2 or more tasks is asked, you should break down the task into smaller tasks"
        "For example, if the task is 'What is the capital of France and what is the languge in Jordan?',"
        "and you have gathered information about the country, you should break down the task into "
        "'capital of France?'in one research and then another task 'language in Jordan?' provive one search term at a time"
    )
    response = llm.invoke(prompt)
    
    # Decision logic - determine next step
    decision = make_decision(state, response.content)
    
    updated_state = AgentState(
        task=state.task,
        memory=state.memory + [f"Planner: {response.content}"],
        next_action=response.content,
        failed_attempts=state.failed_attempts,
        decision=decision
    )
    print(f"Planner decision: {decision}")

    return updated_state
