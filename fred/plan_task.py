from .config import config, APIKeyNotFoundError
import instructor
from openai import OpenAI
from typing import List
from .models import Search, SearchList, SeriesForSearch
from .search_for_single_series import find_relevant_series

try:
    client = instructor.from_openai(OpenAI(api_key=config.get_api_key("OPENAI_API_KEY")))
except APIKeyNotFoundError as e:
    print("API KEY Not Found!")
except Exception as e:
    print(e)

prompt = '''

You are an AI agent whose job it is to plan tasks to solve a user query. Just tell me what to search for in my database (of FRED series), so I can answer the user's query properly. Go through all the steps an economist who knows the FRED database would do step by step. 

Each search is for one series only. give different searches in different search. Give each search at the most specific level possible. If you can give a search to be more specific, do it. 
'''

print(prompt)

search_list:SearchList = client.chat.completions.create(response_model=SearchList, model="gpt-4o", messages=[
    {"role":"system", "content":prompt}, 
    {"role": "user", "content": "the user query is: Compare all the G7 countries by GDP growth this year"}
])

print(search_list)

series: List[List[SeriesForSearch]] = []
for search_query in search_list.queries:
    print(search_query)
    answer = find_relevant_series(query=search_query.query, verbose=True).relevant
    print(answer)
    series.append(answer)

print(series)