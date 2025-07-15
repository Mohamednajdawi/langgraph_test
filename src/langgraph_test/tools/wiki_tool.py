from langchain.tools import WikipediaQueryRun, tool
from langchain.utilities import WikipediaAPIWrapper

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=3, lang="en"))


@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a given query."""
    result = wiki.run(query)
    return result