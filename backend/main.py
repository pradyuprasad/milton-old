from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fred.models import DAG, SearchNode, SeriesForSearch
from fred.plan_task import makeDAG
from fred.search_for_single_series import find_relevant_series
from fred.single_series import ask_questions_about_series

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class QueryRequest(BaseModel):
    query: str

class AnalyzeSeriesRequest(BaseModel):
    query: str
    series_list: List[SeriesForSearch]

@app.post("/api/initial_query")
async def initial_query(request: QueryRequest):
    query = request.query
    if not query:
        raise HTTPException(status_code=400, detail="No query provided")

    print(f"Processing query: {query}")
    
    # Make DAG
    dag = makeDAG(query)
    print(f"Created DAG: {dag}")
    
    # Prepare response
    dag_json = dag.model_dump()

    search_results = {}
    for node in dag.nodes:
        if isinstance(node, SearchNode):
            print(f"Searching for node {node.id}: {node.query}")
            search_results[node.id] = [series.dict() for series in find_relevant_series(node.query, verbose=True)]
            print(f"Search results for node {node.id}: {search_results[node.id]}")
    
    return {
        "dag": dag_json,
        "search_results": search_results
    }

@app.post("/api/analyze_series")
async def analyze_series(request: AnalyzeSeriesRequest):
    series_list = request.series_list
    query = request.query

    try:
        result = ask_questions_about_series(series_list, query)
        print("result is", result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
