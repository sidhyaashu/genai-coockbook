import os
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from scrapegraph_py import Client
from scrapegraphai.graphs import SmartScraperGraph
from davia import Davia

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
sg_api_key = os.getenv("SG")
app = Davia()

class State(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]
    urls: Annotated[list, add_messages]
    extracted: Annotated[list, add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

search_tool = TavilySearch(max_results=2)
scrape_client = Client(api_key=sg_api_key)


def web_search(state: State) -> dict:
    """Node to perform a web search based on the user's input."""
    print("---NODE: Searching Web---")

    tool_results = search_tool.invoke(state["user_input"])

    

    for result in tool_results["results"]:

        return {"urls": [result["url"]]}

    


def scrap_data(state: State) -> dict:
    """Node to scrape data from the URLs found by the web search."""
    print("---NODE: Scraping Data---")


    for url in state["urls"]:
        print(f"Scraping {url}")
        try:
            response = scrape_client.smartscraper(
                website_url=url,
                user_prompt="Extract the main content from this page."
            )
            
            return {"extracted": [response]}
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    


def chatbot(state: State) -> dict:
    """Node to generate a final response using the LLM and scraped data."""
    print("---NODE: Generating Response---")
     

    context = "\n\n---\n\n".join(state["extracted"])

    prompt = f"""Based on the following context, make detaile doc.

    Context:
    {context}

    """

    response = llm.invoke(prompt)
    return {"messages": [response]}



# memory = MemorySaver()

# graph_builder = StateGraph(State)

# graph_builder.add_node("search", web_search)
# graph_builder.add_node("extract", scrap_data)
# graph_builder.add_node("bot", chatbot)

# graph_builder.set_entry_point("search")
# graph_builder.add_edge("search", "extract")
# graph_builder.add_edge("extract", "bot")
# graph_builder.set_finish_point("bot")

# graph = graph_builder.compile(checkpointer=memory)

@app.graph
def hello_graph():
    """
    Advanced langraph chatbot search in web using tavily and then scrap data on url using scrapgraph and then give the data to gemini for better response.
    """
    
    graph_builder = StateGraph(State)

    graph_builder.add_node("search", web_search)
    graph_builder.add_node("extract", scrap_data)
    graph_builder.add_node("bot", chatbot)

    graph_builder.set_entry_point("search")
    graph_builder.add_edge("search", "extract")
    graph_builder.add_edge("extract", "bot")
    graph_builder.set_finish_point("bot")
    return graph_builder



if __name__ == "__main__":
    app.run()