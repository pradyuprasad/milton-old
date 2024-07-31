from .config import config, APIKeyNotFoundError
import instructor
from openai import OpenAI
from typing import List
from .models import Search, SearchList, SeriesForSearch
from .search_for_single_series import find_relevant_series
from .single_series import ask_questions_about_series
import time

try:
    client = instructor.from_openai(OpenAI(api_key=config.get_api_key("OPENAI_API_KEY")))
except APIKeyNotFoundError as e:
    print("API KEY Not Found!")
except Exception as e:
    print(e)

prompt = '''

You are an expert economist AI assistant specializing in the FRED (Federal Reserve Economic Data) database. Your task is to generate a comprehensive list of specific FRED series searches to gather data for answering user queries about economic topics.

Given a user query, your job is to:

1. Analyze the query to identify the main economic topics and indicators involved.
2. Generate a detailed list of FRED series to search for, covering all relevant aspects of the query.
3. Provide the exact FRED series ID for each search when possible.
4. Briefly explain the relevance of each series to the query.

Follow these guidelines for each search:

1. Be as specific as possible in your search suggestions.
2. Include both broad measures and more granular subcategory data when available.
3. Consider related economic indicators that might provide valuable context.

Aim to provide a comprehensive set of searches that would allow for a thorough analysis of the topic in question. Your list should enable the creation of a detailed report covering all aspects mentioned in the user's query.

'''

print("ask your question")
query = input()


start = time.time()

search_list:SearchList = client.chat.completions.create(response_model=SearchList, model="gpt-4o", messages=[
    {"role":"system", "content":prompt}, 
    {"role": "user", "content": f"the user query is:{query} "}
])

print(search_list)

series: List[SeriesForSearch] = []
for search_query in search_list.queries:
    print(search_query)
    answer: List[SeriesForSearch] = find_relevant_series(query=search_query.query, verbose=True).relevant
    print(answer)
    series.extend(answer)

ask_questions_about_series(series_list=series, query=query)

print(f"\n\n\n. The time taken is {time.time() - start} seconds")