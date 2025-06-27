from scrapegraphai.graphs import SmartScraperGraph
import nest_asyncio
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Apply nested event loop support (for Jupyter or already running loops)
nest_asyncio.apply()

# ✅ FIX 1: Use actual OpenAI API key or environment variable
# DO NOT hardcode as "OPENAI_API_KEY"
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")  # Replace with your real key or use dotenv

# ✅ FIX 2: Proper config structure
graph_config = {
   "llm": {
       "api_key": os.getenv("OPENAI_API_KEY"),
       "model": "openai/gpt-4o-mini",
   },
   "verbose": True,
   "headless": False,
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage, including a description of what the company does, founders and social media links.",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# ✅ FIX 3: Use asyncio.run() safely
async def run_scraper():
    return await smart_scraper_graph.run()

result = asyncio.run(run_scraper())
print(result)
