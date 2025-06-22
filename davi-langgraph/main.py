from typing import Annotated
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import random
import os
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from davia import Davia

load_dotenv()

app = Davia()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
)

# ----------------- TOOL FUNCTIONS -----------------

def roll_dice(sides: int = 6) -> str:
    """Roll a dice with a given number of sides and return the result."""
    if sides < 2:
        return "A die must have at least two sides."
    return f"🎲 You rolled a {random.randint(1, sides)} on a {sides}-sided die."

def calculate_health(current_health: int, change: int) -> str:
    """
    Calculate player's new health after taking damage or healing.
    
    Args:
        current_health (int): Player's current health.
        change (int): Amount to change health (positive for healing, negative for damage).
    
    Returns:
        str: Updated health status.
    """
    new_health = max(0, current_health + change)
    return f"❤️ Player's health is now {new_health} HP."

def generate_scenario(theme: str = "fantasy", difficulty: str = "medium") -> str:
    """
    Generate a short, immersive RPG scenario intro based on the theme and difficulty.
    """
    system_prompt = f"""
You are a creative AI storyteller in a role-playing game world.

Your task is to generate an immersive and vivid story **scenario intro** based on:
- Theme: {theme}
- Difficulty: {difficulty}

📜 Guidelines:
1. Match the genre and tone (e.g. fantasy, sci-fi, horror).
2. Base difficulty on:
   - easy: light conflict or discovery
   - medium: moderate stakes, some conflict
   - hard: complex moral choices or dangerous events
3. Use imaginative and descriptive language.
4. Do not resolve the story — set the **opening scene** only.

✍️ Output Format:
- Title (bold, max 10 words)
- 1 paragraph of narrative (max 200 words)

Keep it intriguing and open-ended.
"""
    message = [SystemMessage(content=system_prompt)]
    resp = llm.invoke(message)
    return resp.content

# ----------------- TOOL REGISTRATION -----------------

tools = [roll_dice, calculate_health, generate_scenario]
llm_with_tools = llm.bind_tools(tools)

# ----------------- SYSTEM PROMPT FOR CHAT -----------------

SYSTEM_PROMPT = """
You are a master AI game master in a role-playing game.

Your job is to interact with the player, respond to their actions, and use tools if needed to simulate dice rolls, health tracking, or generate new story scenarios.

Always be immersive, creative, and respond in the voice of an RPG narrator. Use tools when players ask for actions like 'roll a dice', 'check my health', or 'create a new quest'.
"""

# ----------------- CHATBOT NODE -----------------

def chatbot(state: MessagesState):
    return {
        "messages": [
            llm_with_tools.invoke(
                state["messages"] + [SystemMessage(content=SYSTEM_PROMPT)]
            )
        ]
    }

# ----------------- GRAPH BUILDING -----------------

@app.graph
def graph():
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    return graph_builder


if __name__ == "__main__":
    app.run()