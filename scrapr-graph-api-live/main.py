import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from scrapegraph_py import Client

# It's good practice to handle potential import errors, though
# requirements.txt should prevent this.
try:
    from scrapegraphai.graphs import (
        CodeGeneratorGraph,
        CSVScraperGraph,
        CSVScraperMultiGraph,
        DepthSearchGraph,
        DocumentScraperGraph,
        JSONScraperGraph,
        JSONScraperMultiGraph,
        OmniScraperGraph,
        OmniSearchGraph,
        ScriptCreatorGraph,
        ScriptCreatorMultiGraph,
        SearchGraph,
        SearchLinkGraph,
        SmartScraperGraph,
        SmartScraperLiteGraph,
        SmartScraperMultiConcatGraph,
        SmartScraperMultiGraph,
        SmartScraperMultiLiteGraph,
        SpeechGraph,
        XMLScraperGraph,
        XMLScraperMultiGraph,
    )
except ImportError:
    raise ImportError("ScrapeGraphAI is not installed. Please install it with 'pip install scrapegraphai'")

# Create FastAPI app
app = FastAPI(
    title="ScrapeGraphAI API",
    description="A flexible and production-ready REST API for all ScrapeGraphAI graphs.",
    version="1.2.0",
)


# --- Pydantic Models for Requests ---

# Base model to require API key in every request
class APIKeyRequest(BaseModel):
    api_key: str = Field(description="Your GOOGLE API key.")

# Models for endpoints that take prompt and a single source
class BaseRequest(APIKeyRequest):
    prompt: str
    source: str

# Models for endpoints that take prompt and multiple sources
class MultiSourceRequest(APIKeyRequest):
    prompt: str
    sources: List[str]

# Model for search-based endpoints
class SearchRequest(APIKeyRequest):
    prompt: str

# Model for SearchLinkGraph
class SearchLinkRequest(APIKeyRequest):
    source: str

# Model for SmartScraperLiteGraph
class SmartScraperLiteRequest(APIKeyRequest):
    source: str

# Model for SpeechGraph
class SpeechRequest(APIKeyRequest):
    prompt: str
    source: str
    output_path: Optional[str] = "website_summary.mp3"

# Model for graphs that can accept a schema
class SchemaRequest(APIKeyRequest):
    prompt: str
    source: str
    schema_name: str


# --- Pydantic Models for Schemas ---
class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]

class CeoName(BaseModel):
    ceo_name: str = Field(description="The name and surname of the CEO")

class Ceos(BaseModel):
    names: List[CeoName]

class Dish(BaseModel):
    name: str = Field(description="The name of the dish")
    description: str = Field(description="The description of the dish")

class Dishes(BaseModel):
    dishes: List[Dish]

# A dictionary to easily access schemas by name
schemas = {
    "Projects": Projects,
    "Ceos": Ceos,
    "Dishes": Dishes,
}

BASE_MODEL="google_genai/gemini-2.0-flash"


# --- API Endpoints ---
@app.get("/", summary="Root Endpoint", description="Returns a welcome message.")
def read_root():
    return {"message": "Welcome to the ScrapeGraphAI API! Visit /docs for documentation."}

@app.get("/health", summary="Health Check", description="Returns a 200 OK status if the API is running.")
def health_check():
    return {"status": "ok"}


# --- Smart Scraper Endpoints ---
@app.post("/smart_scraper/run", summary="Run SmartScraperGraph", tags=["Smart Scraper"])
def run_smart_scraper(request: BaseRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True,
    }
    try:
        smart_scraper_graph = SmartScraperGraph(prompt=request.prompt, source=request.source, config=graph_config)
        result = smart_scraper_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
# --- Scrape profile by url ---
@app.post("/smart_profile_scraper/run", summary="Run SmartScraperGraph", tags=["Smart Profile Scraper"])
def run_smart_profile_scraper(request: BaseRequest):
    
    api_key = request.api_key
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required.")
    # Initialize the ScrapeGraphAI client with the provided API key
    
    try:
    
        client = Client(api_key=api_key)
        
        response = client.smartscraper(
            website_url=request.source,
            user_prompt=request.prompt
        )
        
        if not response:
            raise HTTPException(status_code=500, detail="No data returned from the scraper.")
        
        return response["result"]
    except Exception as e:
        client.close()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/smart_scraper/run_with_schema", summary="Run SmartScraperGraph with schema", tags=["Smart Scraper"])
def run_smart_scraper_with_schema(request: SchemaRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True,
    }
    schema = schemas.get(request.schema_name)
    if not schema:
        raise HTTPException(status_code=400, detail=f"Schema '{request.schema_name}' not found.")
    try:
        smart_scraper_graph = SmartScraperGraph(prompt=request.prompt, source=request.source, schema=schema, config=graph_config)
        result = smart_scraper_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/smart_scraper_lite/run", summary="Run SmartScraperLiteGraph", tags=["Smart Scraper"])
def run_smart_scraper_lite(request: SmartScraperLiteRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True,
    }
    try:
        smart_scraper_lite_graph = SmartScraperLiteGraph(prompt="", source=request.source, config=graph_config)
        result = smart_scraper_lite_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/smart_scraper_multi/run", summary="Run SmartScraperMultiGraph", tags=["Smart Scraper"])
def run_smart_scraper_multi(request: MultiSourceRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True,
    }
    try:
        smart_scraper_multi_graph = SmartScraperMultiGraph(prompt=request.prompt, source=request.sources, config=graph_config)
        result = smart_scraper_multi_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# ... (similar refactoring for all other multi-scraper endpoints)


# --- Search Endpoints ---
@app.post("/search/run", summary="Run SearchGraph", tags=["Search"])
def run_search(request: SearchRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "max_results": 2, "verbose": True,
    }
    try:
        search_graph = SearchGraph(prompt=request.prompt, config=graph_config)
        result = search_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/search/run_with_schema", summary="Run SearchGraph with schema", tags=["Search"])
def run_search_with_schema(request: SchemaRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "max_results": 2, "verbose": True,
    }
    schema = schemas.get(request.schema_name)
    if not schema:
        raise HTTPException(status_code=400, detail=f"Schema '{request.schema_name}' not found.")
    try:
        search_graph = SearchGraph(prompt=request.prompt, schema=schema, config=graph_config)
        result = search_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/search_link/run", summary="Run SearchLinkGraph", tags=["Search"])
def run_search_link(request: SearchLinkRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True,
    }
    try:
        search_link_graph = SearchLinkGraph(source=request.source, config=graph_config)
        result = search_link_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# --- Omni Scraper Endpoints ---
@app.post("/omni_scraper/run", summary="Run OmniScraperGraph", tags=["Omni Scraper"])
def run_omni_scraper(request: BaseRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model":BASE_MODEL},
        "verbose": True, "headless": True, "max_images": 5,
    }
    try:
        omni_scraper_graph = OmniScraperGraph(prompt=request.prompt, source=request.source, config=graph_config)
        result = omni_scraper_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/omni_search/run", summary="Run OmniSearchGraph", tags=["Omni Scraper"])
def run_omni_search(request: SearchRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "max_results": 2, "max_images": 1, "verbose": True,
    }
    try:
        omni_search_graph = OmniSearchGraph(prompt=request.prompt, config=graph_config)
        result = omni_search_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# --- Code & Script Generator Endpoints ---
@app.post("/code_generator/run", summary="Run CodeGeneratorGraph", tags=["Generators"])
def run_code_generator(request: SchemaRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True, "reduction": 2,
        "max_iterations": {"overall": 5, "syntax": 2, "execution": 2, "validation": 2, "semantic": 2},
        "output_file_name": "generated_code.py",
    }
    schema = schemas.get(request.schema_name)
    if not schema:
        raise HTTPException(status_code=400, detail=f"Schema '{request.schema_name}' not found.")
    try:
        code_generator_graph = CodeGeneratorGraph(prompt=request.prompt, source=request.source, schema=schema, config=graph_config)
        result = code_generator_graph.run()
        return {"code": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# ... (Apply the same pattern to other generator endpoints)


# --- Other Endpoints ---
@app.post("/speech/run", summary="Run SpeechGraph", tags=["Other Graphs"])
def run_speech(request: SpeechRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL, "temperature": 0.7},
        "tts_model": {"api_key": request.api_key, "model": "tts-1", "voice": "alloy"},
        "output_path": request.output_path,
    }
    try:
        speech_graph = SpeechGraph(prompt=request.prompt, source=request.source, config=graph_config)
        result = speech_graph.run()
        return {"summary": result, "audio_file": request.output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/depth_search/run", summary="Run DepthSearchGraph", tags=["Search"])
def run_depth_search(request: BaseRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL},
        "verbose": True, "headless": True, "depth": 2, "only_inside_links": False,
    }
    try:
        depth_search_graph = DepthSearchGraph(prompt=request.prompt, source=request.source, config=graph_config)
        result = depth_search_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# --- Add other endpoints like csv_scraper, document_scraper, etc. following the same pattern ---
# Example for one more to ensure clarity:
@app.post("/xml_scraper/run", summary="Run XMLScraperGraph", tags=["Other Graphs"])
def run_xml_scraper(request: BaseRequest):
    graph_config = {
        "llm": {"api_key": request.api_key, "model": BASE_MODEL}, "verbose": False,
    }
    try:
        # Assuming source is raw XML content for this endpoint
        xml_scraper_graph = XMLScraperGraph(prompt=request.prompt, source=request.source, config=graph_config)
        result = xml_scraper_graph.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# --- Run the app with Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    # This block allows running the app directly with `python main.py`
    # It's mainly for local development. For deployment, you'll use the CMD in the Dockerfile.
    uvicorn.run(app, host="0.0.0.0", port=8000)