import os
from langchain import agents
from langchain.base_language import BaseLanguageModel
from Chemical_material.tools import *
from langchain.tools import PubmedQueryRun

def make_tools(llm: BaseLanguageModel, verbose=False):
    serp_key = os.getenv("SERP_API_KEY")
    if serp_key is None:
        print("Your 'SERP_API_KEY' not found")
    all_tools = agents.load_tools(["python_repl"]) + [PubmedQueryRun()]
    if serp_key:
        all_tools.append(WebSearch())
    return all_tools