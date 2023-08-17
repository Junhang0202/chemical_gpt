import os
from langchain import SerpAPIWrapper
from langchain.tools import BaseTool
from pydantic import validator
from pypdf.errors import PdfReadError
from langchain.embeddings.openai import OpenAIEmbeddings

class WebSearch(BaseTool):
    name = "WebSearch"
    description = (
        "WebSearch is a powerful tool designed to provide accurate answers to questions."
        "For simple questions, input search query, returns snippets from web search. "
    )
    serpapi: SerpAPIWrapper = None

    def __init__(self, search_engine="google"):
        super(WebSearch, self).__init__()
        self.serpapi = SerpAPIWrapper(
            serpapi_api_key=os.getenv("SERP_API_KEY"), 
            search_engine=search_engine
        )

    def _run(self, query: str) -> str:
        try:
            return self.serpapi.run(query)
        except:
            return "Sorry, I can't answer the question, I will try to use another tool"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError()
