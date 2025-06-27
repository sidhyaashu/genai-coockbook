import os
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from scrapegraph_py import Client
from davia import Davia

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
sg_api_key = os.getenv("SG")
app = Davia()

class State(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]
    urls: list  # Changed from Annotated list
    extracted: list  # Changed from Annotated list

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# Fixed: Use TavilySearchAPIWrapper instead of TavilySearch
search_tool = TavilySearch(tavily_api_key=os.getenv("TAVILY_API_KEY"))
scrape_client = Client(api_key=sg_api_key)


def web_search(state: State) -> dict:
    """Node to perform a web search based on the user's input."""
    print("---NODE: Searching Web---")
    
    try:
        # Fixed: Use the correct method and handle response properly
        results = search_tool.results(state["user_input"], max_results=3)
        urls = [result["url"] for result in results if "url" in result]
        
        print(f"Found {len(urls)} URLs")
        return {"urls": urls}
        
    except Exception as e:
        print(f"Error in web search: {e}")
        return {"urls": []}


def scrap_data(state: State) -> dict:
    """Node to scrape data from the URLs found by the web search."""
    print("---NODE: Scraping Data---")
    
    extracted_data = []
    
    # Fixed: Process all URLs, not just return after first one
    for url in state.get("urls", []):
        print(f"Scraping {url}")
        try:
            response = scrape_client.smartscraper(
                website_url=url,
                user_prompt="Extract the main content, key information, and important details from this page."
            )
            
            if response:
                extracted_data.append(f"Content from {url}:\n{response}")
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            extracted_data.append(f"Failed to scrape {url}: {str(e)}")
    
    return {"extracted": extracted_data}


def chatbot(state: State) -> dict:
    """Node to generate a final response using the LLM and scraped data."""
    print("---NODE: Generating Response---")
    
    # Fixed: Handle case where extracted data might be empty
    extracted_data = state.get("extracted", [])
    
    if not extracted_data:
        context = "No data was successfully extracted from the web search."
    else:
        context = "\n\n---\n\n".join(extracted_data)

    prompt = f"""Based on the user's query: "{state['user_input']}" and the following context from web sources, create a detailed and comprehensive response.

    Context from web sources:
    {context}

    Please provide a well-structured, informative response that directly addresses the user's question using the information gathered from the web sources.
    """

    try:
        response = llm.invoke(prompt)
        return {"messages": [response]}
    except Exception as e:
        print(f"Error generating response: {e}")
        return {"messages": [f"Error generating response: {str(e)}"]}


# @app.graph
# def hello_graph():
#     """
#     Advanced langraph chatbot that searches the web using Tavily, scrapes data from URLs using ScrapGraph, 
#     and uses Gemini to generate comprehensive responses.
#     """
    
#     # Fixed: Create a proper StateGraph instance
#     graph_builder = StateGraph(State)

#     # Add nodes
#     graph_builder.add_node("search", web_search)
#     graph_builder.add_node("extract", scrap_data)
#     graph_builder.add_node("bot", chatbot)

#     # Set up the flow
#     graph_builder.set_entry_point("search")
#     graph_builder.add_edge("search", "extract")
#     graph_builder.add_edge("extract", "bot")
#     graph_builder.add_edge("bot", END)  # Fixed: Use END instead of set_finish_point
    
#     # Compile and return the graph
#     memory = MemorySaver()
#     return graph_builder.compile(checkpointer=memory)


# Alternative standalone execution (if not using Davia)
def run_standalone(user_query: str):
    """Run the graph standalone without Davia framework"""
    memory = MemorySaver()
    
    graph_builder = StateGraph(State)
    graph_builder.add_node("search", web_search)
    graph_builder.add_node("extract", scrap_data)
    graph_builder.add_node("bot", chatbot)
    graph_builder.set_entry_point("search")
    graph_builder.add_edge("search", "extract")
    graph_builder.add_edge("extract", "bot")
    graph_builder.add_edge("bot", END)
    
    graph = graph_builder.compile(checkpointer=memory)
    
    # Run the graph
    config = {"configurable": {"thread_id": "1"}}
    result = graph.invoke(
        {"user_input": user_query, "messages": [], "urls": [], "extracted": []},
        config=config
    )
    
    return result


if __name__ == "__main__":
    # Choose execution method based on your needs
    
    # Option 1: Run with Davia framework
    # app.run()
    
    # Option 2: Run standalone (uncomment to test)
    test_query = "What are the latest developments in AI technology?"
    result = run_standalone(test_query)
    print("Final result:", result)
    
    
    
    