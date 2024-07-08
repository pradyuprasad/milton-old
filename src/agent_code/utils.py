import os
import requests
from dotenv import load_dotenv
import time
from typing import Dict, Any, List, Tuple, Type
from enum import Enum
from groq import Groq


load_dotenv()
HUGGINGFACE_API_KEY_2= os.getenv('HUGGINGFACE_API_KEY_2')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
client = Groq(
    api_key=os.environ.get('GROQ_API_KEY'),
)


def convert_SQL_answer_to_list(input: List[tuple[str]]) -> List[str]:
    return list(map(lambda x: x[0], input))


import requests
import time
from typing import Dict, List, Any

def query_model(query: str, labels: List[str]) -> Dict[str, Any]:
    print(labels)
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": query,
        "parameters": {"candidate_labels": labels}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Handling rate limits and server unavailability
    if response.status_code in (503, 429):
        print("503/429 error, retrying with the second API key...")
        headers["Authorization"] = f"Bearer {HUGGINGFACE_API_KEY_2}"
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to process request, server responded with status code: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Failed to process request, server responded with status code: {response.status_code}")
    
    # Attempt to parse the JSON response
    try:
        output:Dict[str, Any] = response.json()
    except ValueError:
        raise Exception("Failed to decode JSON from response")
    
    # Handle errors reported by the API
    if 'error' in output:
        if 'estimated_time' in output:
            estimated_time = output['estimated_time']
            # Ensure estimated_time is not a list
            if isinstance(estimated_time, list):
                if estimated_time:  # Check if list is not empty
                    estimated_time = estimated_time[0]  # Assuming you want the first element
                else:
                    raise Exception("Estimated time list is empty")
            # Convert to integer
            try:
                estimated_time = int(estimated_time)
            except ValueError:
                raise Exception("Estimated time is not a valid integer")
            print("Sleeping for", estimated_time, "seconds")
            time.sleep(estimated_time)
            return query_model(query, labels)  # Recursive call after sleep
        else:
            raise Exception(output['error'])
    
    return output



def get_top_labels(output:Dict[str, List[str]], top_n:int=3) -> List[Tuple[str, str]]:
    if 'labels' in output and 'scores' in output:
        sorted_labels = sorted(zip(output['labels'], output['scores']), key=lambda x: x[1], reverse=True)
        return sorted_labels[:top_n]
    return []

def classify_query(query_text: str, candidate_labels: List[str]) -> List[Tuple[str, str]]:
    print("Candidate labels:", candidate_labels)
    all_top_labels = []
    # Process labels in batches of 10
    for i in range(0, len(candidate_labels), 10):
        batch = candidate_labels[i:i+10]
        if not batch:
            break
        print("Running iteration", int(i + 1) // 10)
        output = query_model(query=query_text, labels=batch)
        top_labels = get_top_labels(output)
        all_top_labels.extend(top_labels)

    # Sort all top labels collected from each batch to get the highest scoring labels
    all_top_labels = sorted(all_top_labels, key=lambda x: x[1], reverse=True)

    # Now take the top labels from the sorted list and run a final query to re-evaluate them
    final_candidates = [label for label, _ in all_top_labels[:10]]  # Taking the top 10 overall labels
    if final_candidates:
        final_output = query_model(query=query_text, labels=final_candidates)
        # Get and return the top labels from this final output
        return get_top_labels(final_output)
    return all_top_labels[:3]  # Return the top 3 if no further query is made

def add_unsure_member(enum_class: Type[Enum]) -> Type[Enum]:
    # Create a new enum with the same members as the existing one plus 'UNSURE'
    new_members = {name: member.value for name, member in enum_class.__members__.items()}
    new_members['UNSURE'] = "Unsure"
    return Enum(enum_class.__name__, new_members)


def GPT_classify_query(old_enum: Type[Enum]):
    new_enum = add_unsure_member(old_enum)
