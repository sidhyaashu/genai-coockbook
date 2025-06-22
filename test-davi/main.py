from davia import Davia
from langgraph.graph import StateGraph, START, END, MessagesState


# Define a simple node
def start(state: MessagesState) -> MessagesState:
    return {"messages": [{"role": "ai", "content": "Hello, how can I help you today?"}]}


# Create and expose the graph
app = Davia()


@app.graph
def hello_graph():
    """
    A minimal LangGraph agent that returns a greeting.
    """
    graph = StateGraph(MessagesState)
    graph.add_node("start", start)
    graph.add_edge(START, "start")
    graph.add_edge("start", END)
    return graph


#  Launch the server
if __name__ == "__main__":
    app.run()