import chromadb
import os
from typing import List, Dict
import instructor
from pydantic import BaseModel
from .config import config, APIKeyNotFoundError
from openai import OpenAI
from groq import Groq

print("Imported libraries")

# Initialize Chroma client with persistent storage
chroma_persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)

# Get the collection
collection = chroma_client.get_collection("fred-economic-series")

class Keywords(BaseModel):
    word: List[str]

try:
    FRED_API_KEY = config.get_api_key('FRED_API_KEY')
    OPENAI_API_KEY = config.get_api_key("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    client = Groq(api_key=config.get_api_key("GROQ_API_KEY"))
    instructor_client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
except APIKeyNotFoundError as e:
    raise e

def extract_keyword(user_query: str) -> Keywords:
    return instructor_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Keywords,
        messages=[
            {"role": "system", "content": """
You are an expert in economic terminology and the FRED (Federal Reserve Economic Data) database. Your task is to convert user queries into the most appropriate search terms for the FRED database.
            """},
            {"role": "user", "content": f"""
Convert the following query into search terms for the FRED database:
"{user_query}"
Follow these rules strictly:
1. Provide only full terms as they would appear in the FRED database. For example, use "Gross Domestic Product" instead of "GDP".
2. Expand all common economic acronyms to their full forms.
3. Focus on specific economic indicators, measurements, or concepts.
4. Provide at most 3 key terms, prioritizing specificity and relevance to the FRED database.
5. Do not include general words like "current", "rate", or country names unless they are part of a specific economic term.
6. If the query mentions a specific country, include the full country name as part of the relevant economic term(s).
Respond with only the list of search terms, nothing else.
            """}
        ]
    )

def search_series_by_keyword(keywords: List[str], n_results: int = 5) -> List[Dict[str, str]]:
    query = " ".join(keywords)
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    series_list = []
    for i in range(len(results['ids'][0])):
        series = {
            'fred_id': results['ids'][0][i],
            'title': results['metadatas'][0][i]['title'],
            'units': results['metadatas'][0][i]['units'],
            'frequency': results['metadatas'][0][i]['frequency'],
            'seasonal_adjustment': results['metadatas'][0][i]['seasonal_adjustment'],
            'last_updated': results['metadatas'][0][i]['last_updated'],
            'popularity': results['metadatas'][0][i]['popularity'],
            'tags': results['metadatas'][0][i]['tags']
        }
        series_list.append(series)
    
    return series_list

def print_series_list(series_list: List[Dict[str, str]]) -> None:
    for series in series_list:
        print(f"FRED ID: {series['fred_id']}")
        print(f"Title: {series['title']}")
        print(f"Popularity: {series['popularity']}")
        print(f"Units: {series['units']}")
        print(f"Frequency: {series['frequency']}")
        print(f"Seasonal Adjustment: {series['seasonal_adjustment']}")
        print(f"Last Updated: {series['last_updated']}")
        print(f"Tags: {series['tags']}\n")
        print("----------------------------")

if __name__ == "__main__":
    query = "What is the current inflation rate in the US"
    print(f"\nQuery: {query}")
    keyword_list = extract_keyword(query)
    print("Extracted keywords:", keyword_list.word)
    search_results = search_series_by_keyword(keyword_list.word)
    print("\nSearch Results:")
    print_series_list(search_results)