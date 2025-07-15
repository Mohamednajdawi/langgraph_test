import re

from nodes.state_agent import AgentState
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0.2)

def examiner_node(state: AgentState) -> AgentState:
    prompt = (
        f"You are an examiner. You are given a task and a summary of the research. You need to decide if the summary is correct. "
        f"Task: {state.task}\n\n"
        f"Summary: {state.memory}\n\n"
        "return 'correct' if the summary is correct, otherwise return 'planner' to replan and research the task again"
        "if the summary include (not specified in the research) return 'planner'"
        "otherwise return 'correct'"
    )
    response = llm.invoke(prompt)
    response_content = response.content
    print(f"Examiner response: {response_content}")
    if "correct" in response_content.lower():
        state.decision = "correct"
    else:
        state.decision = "planner"
    return state
