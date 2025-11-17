"""
Orchestrator Agent Service
Creates and manages the intelligent agent
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document
from datetime import datetime

from backend.core.config import settings
from backend.services.vector_store import vector_store_service


class AgentService:
    """Service for orchestrator agent operations"""
    
    def __init__(self):
        """Initialize agent service"""
        self.web_search = DuckDuckGoSearchRun()
    
    def create_agent(
        self,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ):
        """Create the orchestrator agent with user-specific credentials"""
        # Create model with user's Google API key
        model = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            google_api_key=google_api_key
        )
        
        # Get user-specific vector store
        vector_store = vector_store_service.get_or_create_collection(
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database
        )
        
        # Tool 1: Retrieve from knowledge base
        @tool(response_format="content_and_artifact")
        def retrieve_knowledge(query: str):
            """Search the local knowledge base for relevant information. Use this FIRST before web search."""
            try:
                retrieved_docs = vector_store.similarity_search(query, k=settings.RETRIEVAL_K)
                
                if not retrieved_docs:
                    return "No relevant documents found in knowledge base. Consider using web search.", []
                
                serialized = "\n\n".join(
                    (f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                     f"Content: {doc.page_content}")
                    for doc in retrieved_docs
                )
                
                return serialized, retrieved_docs
            except Exception as e:
                return f"Error retrieving from knowledge base: {str(e)}", []
        
        # Tool 2: Web search (fallback)
        @tool
        def search_web(query: str):
            """Search the web for current information when knowledge base doesn't have the answer. Use this when retrieve_knowledge returns no relevant results."""
            try:
                results = self.web_search.run(query)
                return f"Web Search Results:\n{results}"
            except Exception as e:
                return f"Error performing web search: {str(e)}"
        
        # Tool 3: Index new knowledge
        @tool
        def index_new_knowledge(content: str, source: str = "web_search"):
            """Store new information discovered from web search into the knowledge base for future use."""
            try:
                metadata = {
                    "source": source,
                    "indexed_at": datetime.now().isoformat(),
                    "type": "web_search_result"
                }
                chunks = vector_store_service.index_document(
                    user_id=user_id,
                    google_api_key=google_api_key,
                    chromadb_api_key=chromadb_api_key,
                    chromadb_tenant=chromadb_tenant,
                    chromadb_database=chromadb_database,
                    content=content,
                    metadata=metadata
                )
                return f"Successfully indexed {chunks} chunks into knowledge base"
            except Exception as e:
                return f"Error indexing knowledge: {str(e)}"
        
        # Create orchestrator agent with all tools
        tools = [retrieve_knowledge, search_web, index_new_knowledge]
        
        system_prompt = """You are an intelligent orchestrator agent for a knowledge base system.

Your workflow:
1. ALWAYS try retrieve_knowledge FIRST to check the local knowledge base
2. If no relevant information found (empty results or irrelevant), use search_web to find current information
3. When you find useful information from web search, use index_new_knowledge to store it for future queries
4. Provide comprehensive answers citing your sources

Guidelines:
- Prefer local knowledge base over web search when available
- Always cite whether information came from knowledge base or web search
- When using web search, automatically index useful findings
- Be transparent about what you know vs what you're searching for
- Combine information from multiple sources when relevant"""
        
        agent = create_agent(
            model,
            tools=tools,
            system_prompt=system_prompt
        )
        
        return agent, vector_store


# Global instance
agent_service = AgentService()
