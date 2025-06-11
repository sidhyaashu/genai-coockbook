from google.adk.agents import Agent
from google.adk.tools import google_search
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
model = "gemini-2.0-flash-live-001"

root_agent = Agent(

   name="basic_search_agent",

   model=model,


   description="Agent to answer questions using Google Search.",

   instruction="You are an expert researcher. You always stick to the facts.",
   tools=[google_search]
)