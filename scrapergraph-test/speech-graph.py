import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

FILE_NAME = "website_summary.mp3"
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(curr_dir, FILE_NAME)

openai_key = os.getenv("OPENAI_API_KEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "openai/gpt-4o",
        "temperature": 0.7,
    },
    "tts_model": {
        "api_key": openai_key,
        "model": "tts-1",
        "voice": "alloy"
    },
    "output_path": output_path,
}

speech_graph = SpeechGraph(
    prompt="Make a detailed audio summary of the projects.",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result)