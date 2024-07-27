import chromadb
import os
from typing import List, Dict, Set
import instructor
from pydantic import BaseModel
from .config import config, APIKeyNotFoundError
from openai import OpenAI
from groq import Groq
from .models import SeriesForSearch
from .database import Database, DatabaseConnectionError
chroma_client_temp = chromadb.Client()
series_collection = chroma_client_temp.create_collection(name="temp_series_collection")

print("Imported libraries")

# Initialize Chroma client with persistent storage
chroma_persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)

    
# Get the collection
collection = chroma_client.get_collection("fred-economic-series")
#tags_collection = chroma_client.get_collection("fred-tags")

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
5. Do not include general words like "current", "rate" unless they are part of a specific economic term.
6. If the query mentions a specific country, include the full country name as part of the relevant economic term(s).
Respond with only the list of search terms, nothing else.
            """}
        ]
    )

def search_series_by_keyword(keywords: List[str], n_results: int = 5, query:str = None) -> Set[SeriesForSearch]:
    if not query:
        query = " ".join(keywords)
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    series_list = set()
    for i in range(len(results['ids'][0])):
        series = SeriesForSearch(fred_id=results['ids'][0][i], title=results['metadatas'][0][i]['title'], units=results['metadatas'][0][i]['units'], popularity=results['metadatas'][0][i]['popularity'], relevance_lower_better=results['distances'][0][i])
        series_list.add(series)
    
    return series_list

def search_tags_by_keyword(keywords: List[str], n_results:int = 5) -> None:
    '''
    results = tags_collection.query(
        query_texts=keywords,
        n_results=n_results
    )
    tags_ouputs = set()
    for tag_list in results['documents']:
        for tag in tag_list[:3]:
            tags_ouputs.add(tag)
    print(results)
    tags_ouputs = list(tags_ouputs)
    return tags_ouputs
    '''

def get_series_from_tags(tags: List[str]) -> Set[SeriesForSearch]:
    cursor = Database.get_cursor()
    placeholders = ','.join('?' for _ in tags)
    cursor.execute(f'''
    SELECT s.fred_id, s.title, s.units FROM series s
    JOIN series_tags st ON s.id = st.series_id
    JOIN tags t ON st.tag_id = t.id
    WHERE t.name IN ({placeholders})
    ''', tags)

    ans = cursor.fetchall()
    
    # Create a new client and collection
    temp_client = chromadb.Client()
    temp_collection = temp_client.create_collection(name="temp_tag_series")

    # Process series and add to collection in one pass
    seen_ids = set()
    for row in ans:
        fred_id, title, units = row
        if fred_id not in seen_ids:
            seen_ids.add(fred_id)
            document = f"{title} {units}".lower()
            temp_collection.add(
                documents=[document],
                metadatas=[{"fred_id": fred_id, "title": title, "units": units}],
                ids=[fred_id]
            )
            print(f"Added: FRED ID: {fred_id}, Title: {title}, Units: {units}")

    # Query the collection if we added any documents
    if seen_ids:
        query = " ".join(tags)
        results = temp_collection.query(
            query_texts=[query],
            n_results=min(5, len(seen_ids))
        )
        final_set = set()
        for i in range(len(results['ids'][0])):
            series = SeriesForSearch(fred_id=results['ids'][0][i], title=results['metadatas'][0][i]['title'], units=results['metadatas'][0][i]['units'], popularity=results['metadatas'][0][i]['popularity'])
            final_set.add(series)

    else:
        final_set = set()

    # Clean up
    #del temp_client
    del seen_ids

    return final_set



def print_series_list(series_list:List[SeriesForSearch]) -> None:
    series_list = list(filter(lambda x: x.relevance_lower_better <= 1, series_list))
    series_list.sort(key=lambda x: x.relevance_lower_better)
    for series in series_list:
        print("id:", series.fred_id)
        print("title:", series.title)
        print("popularity:", series.popularity)
        print("units:", series.units)
        print("relevance:", series.relevance_lower_better)
        print("\n\n")
        print("------------------------")
        

if __name__ == "__main__":
    firstTime = True
    while True:
        if not firstTime:
            print("\n\n")
        print("What is your query?")
        query = input()
        print(f"\nQuery: {query}")
        keyword_list = extract_keyword(query)
        print("Extracted keywords:", keyword_list.word)
        search_results = search_series_by_keyword(keyword_list.word, n_results=5, )        
        print_series_list(list(search_results))
        firstTime = False