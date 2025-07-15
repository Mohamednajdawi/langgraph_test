from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=3, lang="en"))


@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a given query."""
    result = wiki.invoke(query)
    return result