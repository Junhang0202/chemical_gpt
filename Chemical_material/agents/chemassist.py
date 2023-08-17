import langchain
import nest_asyncio
from langchain import PromptTemplate, chains
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from rmrkl import ChatZeroShotAgent, RetryAgentExecutor

from .prompts import FORMAT_INSTRUCTIONS, QUESTION_PROMPT, REPHRASE_TEMPLATE, SUFFIX
from .tools import make_tools

def _make_llm(model, temp, verbose):
    if model.startswith("gpt-4"):
        llm = langchain.chat_models.ChatOpenAI(
            temperature=temp,
            model_name=model,
            request_timeout=10000,
            streaming=True if verbose else False,
            callbacks=[StreamingStdOutCallbackHandler()] if verbose else [None]
        )
    else:
        raise ValueError(f"Sorry,here we only support for gpt-4 model")
    return llm

class Chembot:
    def __init__(
        self,
        tools=None,
        model="gpt-4-0613",
        tools_model="gpt-4-0613",
        temp=0.1,
        max_iterations=40,
        verbose=True,
    ):
        self.llm = _make_llm(model,temp,verbose)
        if tools is None:
            tools_llm = _make_llm(tools_model,temp,verbose)
            tools = make_tools(tools_llm,verbose=verbose)
        # Initialize agent
        self.agent_executor = RetryAgentExecutor.from_agent_and_tools(
            tools=tools,
            agent=ChatZeroShotAgent.from_llm_and_tools(
                self.llm,
                tools,
                suffix=SUFFIX,
                format_instructions=FORMAT_INSTRUCTIONS,
                question_prompt=QUESTION_PROMPT,
            ),
            verbose=True,
            max_iterations=max_iterations,
            return_intermediate_steps=True,
        )

        rephrase = PromptTemplate(
            input_variables=["question", "agent_ans"], template=REPHRASE_TEMPLATE
        )

        self.rephrase_chain = chains.LLMChain(prompt=rephrase, llm=self.llm)

    nest_asyncio.apply() 

    def run(self, prompt):
        
        outputs = self.agent_executor({"input": prompt})
        intermed = outputs["intermediate_steps"]

        final = ""
        for step in intermed:
            final += f"Thought: {step[0].log}\n" f"Observation: {step[1]}\n"
        final += f"Final Answer: {outputs['output']}\n"

        rephrased = self.rephrase_chain.run(question=prompt, agent_ans=final)
        print(f"ChemCrow output: {rephrased}")
        return outputs['output']
        return rephrased

    def run_sc(self,prompt):
        tool_list = ["PubMed", "WebSearch"]
        prompt_list = []
        positive = 0
        negative = 0
        for toolname in tool_list:
            formatted_prompt = prompt+f" Plase use {toolname} tool and only answer yes or no."
            answer = self.run(formatted_prompt).lower()
            print(f"\n{toolname} Result: {answer}")
            if "yes" in answer.lower():
                positive += 1
            else:
                negative += 1
        if positive >= negative:
            voting_result = "Yes"
        else:
            voting_result = "No"
        return voting_result            
                
            
                        
            