# services/chatbot.py
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Literal
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class HybridSearchChatbot:
    def __init__(self, openai_api_key: str):
        logger.debug("Initializing HybridSearchChatbot")
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            temperature=0.7,
            model_name="gpt-3.5-turbo",
        )
        self.search_wrapper = DuckDuckGoSearchAPIWrapper()
        
        self.tools = [
            Tool(
                name="Web Search",
                func=self._web_search,
                description="Useful for searching current information on the internet"
            ),
            Tool(
                name="AI Response",
                func=self._ai_response,
                description="Use for general knowledge questions"
            )
        ]
        
        self._setup_agent()
    
    def _setup_agent(self):
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful chatbot that can search the web or use AI to answer questions."),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            self.agent = create_openai_functions_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=2
            )
        except Exception as e:
            logger.error(f"Error setting up agent: {str(e)}")
            raise

    def _web_search(self, query: str) -> str:
        logger.debug(f"Performing web search for: {query}")
        try:
            result = self.search_wrapper.run(query)
            logger.debug(f"Web search result: {result}")
            return result
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            raise

    def _ai_response(self, query: str) -> str:
        logger.debug(f"Getting AI response for: {query}")
        try:
            response = self.llm.invoke(query)
            logger.debug(f"AI response: {response.content}")
            return response.content
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            raise

    def _determine_search_type(self, query: str) -> Literal["web", "ai"]:
        logger.debug(f"Determining search type for query: {query}")
        try:
            prompt = f"Is this query about current events or real-time information? Answer with just 'web' or 'ai': {query}"
            response = self.llm.invoke(prompt)
            search_type = "web" if "web" in response.content.lower().strip() else "ai"
            logger.debug(f"Determined search type: {search_type}")
            return search_type
        except Exception as e:
            logger.error(f"Error determining search type: {str(e)}")
            return "ai"

    def query(self, user_input: str) -> str:
        logger.debug(f"Processing query: {user_input}")
        try:
            search_type = self._determine_search_type(user_input)
            
            if search_type == "web":
                logger.debug("Using web search")
                try:
                    result = self.agent_executor.invoke({"input": user_input})
                    logger.debug(f"Web search result: {result}")
                    return result["output"]
                except Exception as e:
                    logger.error(f"Web search error: {str(e)}")
                    return self._ai_response(user_input)  # Fallback to AI
            else:
                logger.debug("Using AI response")
                return self._ai_response(user_input)
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return f"I apologize, but I'm having trouble processing your request: {str(e)}"