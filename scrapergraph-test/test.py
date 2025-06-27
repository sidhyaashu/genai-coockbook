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

load_dotenv()
memory = MemorySaver()


class State(TypedDict):
    user_input:str
    messages: Annotated[list, add_messages]
    urls:list[str]
    extracted:list[str]
    
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
sg=os.getenv("SG")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
tool = TavilySearch(max_results=2)
tools = [tool]


def web_search(state:State):
    tools_res = tool.invoke(state["user_input"])
    
    urls = []

    for result in tools_res["results"]:
        urls.append(result["url"])
        
    return{
        "urls":urls,
    }
    
def scrap_data(state:State):
    client = Client(api_key=sg)
    
    res = []
    for i in state["url"]:
        response = client.smartscraper(
            website_url=i,
            user_prompt="Extract everything about this provided link"
        )
        
        res.append(response)
        
    return {
        "extracted":res
    }
    
def chatbot(state: State):
    return {"messages": [llm.invoke(state["extracted"])]}


def startGraph():
    graph_builder = StateGraph(State)
    
    graph_builder.add_node("search",web_search)
    graph_builder.add_node("extract",scrap_data)
    graph_builder.add_node("bot",chatbot)

    graph_builder.set_entry_point("search")
    graph_builder.add_edge("search","extract")
    graph_builder.add_edge("extract","bot")
    graph_builder.set_finish_point("bot")


    graph = graph_builder.compile(checkpointer=memory)
    
    return graph