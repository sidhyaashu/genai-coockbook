import os 
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from scrapegraph_py import Client
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
memory = MemorySaver()


class State(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]
    urls: list[str]
    extracted: list[str]
    
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
sg = os.getenv("SG")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
tool = TavilySearch(max_results=4)


def web_search(state: State):
    """Search the web for relevant URLs based on user input"""
    print(f"🔍 Searching for: {state['user_input']}")
    
    try:
        tools_res = tool.invoke(state["user_input"])
        urls = [result["url"] for result in tools_res["results"]]
        
        print(f"📋 Found {len(urls)} URLs")
        return {"urls": urls}
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        return {"urls": []}


def scrape_data(state: State):
    """Scrape data from the found URLs"""
    print(f"🕷️ Scraping {len(state['urls'])} URLs...")
    
    client = Client(api_key=sg)
    extracted_data = []
    
    for i, url in enumerate(state["urls"]):
        try:
            print(f"  Processing URL {i+1}/{len(state['urls'])}: {url}")
            
            response = client.smartscraper(
                website_url=url,
                user_prompt="Extract the main content, key information, and relevant details from this webpage"
            )
            
            # Handle both string and dict responses
            if isinstance(response, dict):
                content = response.get('content', str(response))
            else:
                content = str(response)
                
            extracted_data.append(f"URL: {url}\nContent: {content}\n" + "="*50)
            
        except Exception as e:
            print(f"  ⚠️ Error scraping {url}: {e}")
            extracted_data.append(f"URL: {url}\nError: Could not extract content from this URL\n" + "="*50)
    
    return {"extracted": extracted_data}


def chatbot(state: State):
    """Generate AI response based on extracted data and user input"""
    print("🤖 Generating AI response...")
    
    # Combine extracted data into a single context
    context = "\n\n".join(state["extracted"]) if state["extracted"] else "No data was extracted from the URLs."
    
    # Create a comprehensive prompt
    prompt = f"""
User Question: {state['user_input']}

Based on the following extracted web content, please provide a comprehensive and helpful answer:

{context}

Please provide a clear, well-structured response that directly addresses the user's question using the information found in the web content. If the extracted content doesn't fully answer the question, please indicate what information is missing.
"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [response]}
    
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        error_msg = AIMessage(content=f"I apologize, but I encountered an error while processing your request: {e}")
        return {"messages": [error_msg]}


def create_graph():
    """Create and return the LangGraph workflow"""
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("search", web_search)
    graph_builder.add_node("extract", scrape_data)
    graph_builder.add_node("bot", chatbot)

    # Define the flow
    graph_builder.set_entry_point("search")
    graph_builder.add_edge("search", "extract")
    graph_builder.add_edge("extract", "bot")
    graph_builder.set_finish_point("bot")

    # Compile with memory
    graph = graph_builder.compile(checkpointer=memory)
    return graph


def run_research_assistant(user_query: str, thread_id: str = "default"):
    """Run the research assistant with a user query"""
    print(f"🚀 Starting research for: '{user_query}'")
    print("="*60)
    
    graph = create_graph()
    
    # Initial state
    initial_state = {
        "user_input": user_query,
        "messages": [],
        "urls": [],
        "extracted": []
    }
    
    # Configure thread
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Run the graph
        result = graph.invoke(initial_state, config)
        
        print("\n" + "="*60)
        print("📄 FINAL RESULT:")
        print("="*60)
        
        if result["messages"]:
            final_message = result["messages"][-1]
            print(final_message.content)
        else:
            print("No response generated.")
            
        return result
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Example queries
    queries = [
        "What are the latest developments in AI research?",
        "How does climate change affect ocean temperatures?",
        "What are the best practices for Python web scraping?"
    ]
    
    # You can test with any of these queries
    user_query = input("Enter your research question: ") or queries[0]
    
    result = run_research_assistant(user_query)