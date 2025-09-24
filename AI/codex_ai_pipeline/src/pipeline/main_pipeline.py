from typing import Dict, Any, Optional
import asyncio
import os

# Best‑effort environment loading (safe if dotenv missing)
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dep
    def load_dotenv(*args, **kwargs):
        return False

# Optional LangChain imports with graceful fallbacks
try:
    from langchain_openai import ChatOpenAI as _ChatOpenAI  # type: ignore
    from langchain.tools import Tool as _Tool  # type: ignore
except Exception:
    _ChatOpenAI = None
    _Tool = None

# Lightweight fallbacks so the pipeline can run without LangChain
class MockChatOpenAI:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7, max_tokens: int = 1000, **_: Any):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, prompt: Any) -> str:
        # Simple echo behavior for local/dev use
        return f"[Mock {self.model}] {str(prompt)[:200]}"

class SimpleTool:
    def __init__(self, name: str, description: str, func):
        self.name = name
        self.description = description
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

# Load environment variables if available
load_dotenv()

# Mock classes for missing components
class MockDocumentProcessor:
    def __init__(self):
        pass

class MockVectorSearch:
    def search(self, query):
        return {"documents": [{"document": f"Mock document for: {query}"}]}

class MockMultiAgentSystem:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
    
    def execute_workflow(self, query):
        return {"output": f"Mock AI response for: {query}"}

class MockPipelineEvaluator:
    def evaluate_response(self, query, response, context):
        return {"score": 0.8, "reasoning": "Mock evaluation"}

class MockPipelineMonitor:
    def __init__(self):
        pass

class MockVoiceProcessor:
    def __init__(self):
        pass

# Try to import real components, fallback to mocks
try:
    from .rag.document_processor import DocumentProcessor
    from .rag.vector_search import VectorSearch
    from .agents.multi_agent_system import MultiAgentSystem
    from .evaluation.evaluator import PipelineEvaluator
    from .monitoring.monitor import PipelineMonitor
    from .voice.voice_processor import VoiceProcessor
except ImportError:
    DocumentProcessor = MockDocumentProcessor
    VectorSearch = MockVectorSearch
    MultiAgentSystem = MockMultiAgentSystem
    PipelineEvaluator = MockPipelineEvaluator
    PipelineMonitor = MockPipelineMonitor
    VoiceProcessor = MockVoiceProcessor

class CodexAIPipeline:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.setup_components()
    
    def _get_default_config(self):
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    def setup_components(self):
        # Initialize LLM with graceful fallback if LangChain or API key is unavailable
        llm_kwargs = {
            "model": self.config["model_name"],
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
        }
        api_key = self.config.get("openai_api_key")

        if _ChatOpenAI is not None:
            try:
                if api_key:
                    llm_kwargs["openai_api_key"] = api_key
                self.llm = _ChatOpenAI(**llm_kwargs)
            except Exception:
                self.llm = MockChatOpenAI(**llm_kwargs)
        else:
            self.llm = MockChatOpenAI(**llm_kwargs)

        # Initialize core components first
        self.doc_processor = DocumentProcessor()
        self.vector_search = VectorSearch()

        # Initialize tools (bound to initialized vector_search)
        self.tools = self._create_tools(self.vector_search)

        # Remaining components
        self.agent_system = MultiAgentSystem(self.llm, self.tools)
        self.evaluator = PipelineEvaluator()
        self.monitor = PipelineMonitor()
        self.voice_processor = VoiceProcessor()
    
    def _create_tools(self, vector_search):
        def search_tool(query: str) -> str:
            """Search for information using vector search"""
            try:
                results = vector_search.search(query)
                return str(results)
            except Exception as e:
                return f"Search error: {str(e)}"
        
        def web_search_tool(query: str) -> str:
            """Search the web for information"""
            return f"Web search results for: {query}"

        ToolImpl = _Tool if _Tool is not None else SimpleTool

        return [
            ToolImpl(
                name="vector_search",
                description="Search through documents using vector similarity",
                func=search_tool,
            ),
            ToolImpl(
                name="web_search",
                description="Search the web for current information",
                func=web_search_tool,
            ),
        ]
    
    async def process_query(self, query: str, context: Optional[str] = None):
        try:
            # Step 1: Retrieve relevant documents only when no explicit context provided
            retrieved_context: Optional[str] = None
            if not context:
                try:
                    relevant_docs = self.vector_search.search(query)
                    retrieved_context = "\n".join(
                        [doc.get("document", "") for doc in relevant_docs.get("documents", [])]
                    )
                except Exception:
                    retrieved_context = None
            
            # Step 2: Execute agentic workflow
            result = self.agent_system.execute_workflow(query)
            
            # Step 3: Evaluate response
            final_context = context if context is not None else (retrieved_context or "")
            evaluation = self.evaluator.evaluate_response(
                query, result.get("output", str(result)), final_context
            )
            
            return {
                "query": query,
                "response": result.get("output", str(result)),
                "evaluation": evaluation,
                "context": final_context or None,
            }
        except Exception as e:
            return {
                "query": query,
                "response": f"Error processing query: {str(e)}",
                "evaluation": {"score": 0, "error": str(e)},
                "context": context,
            }

# Example usage
if __name__ == "__main__":
    async def main():
        pipeline = CodexAIPipeline()
        result = await pipeline.process_query("What is artificial intelligence?")
        print(f"Query: {result['query']}")
        print(f"Response: {result['response']}")
        print(f"Evaluation: {result['evaluation']}")
    
    asyncio.run(main())
