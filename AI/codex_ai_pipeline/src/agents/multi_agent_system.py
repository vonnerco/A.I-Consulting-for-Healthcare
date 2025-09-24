from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate

class MultiAgentSystem:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.setup_agents()
    
    def setup_agents(self):
        # Research Agent
        research_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research agent. Use tools to gather information."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        self.research_agent = create_openai_functions_agent(
            self.llm, self.tools, research_prompt
        )
        
        # Analysis Agent
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an analysis agent. Analyze information and provide insights."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        self.analysis_agent = create_openai_functions_agent(
            self.llm, self.tools, analysis_prompt
        )
    
    def execute_workflow(self, query: str):
        # Step 1: Research
        research_result = self.research_agent.invoke({"input": query})
        
        # Step 2: Analysis
        analysis_input = f"Analyze this research: {research_result}"
        analysis_result = self.analysis_agent.invoke({"input": analysis_input})
        
        return analysis_result
