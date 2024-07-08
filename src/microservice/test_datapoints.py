import requests
import time

print("What's your query?")
query = input()
#url = "http://0.0.0.0:10000/select-datapoints"
url = 'https://sgdataproject-microservice.onrender.com/select-datapoints'

message_data = {
    "query": query
}

start_time = time.time()  # Record the start time

ans = requests.post(url=url, json=message_data)

end_time = time.time()  # Record the end time

elapsed_time = end_time - start_time  # Calculate the elapsed time

print(f"Status code: {ans.status_code}")
print(f"Response: {ans.json()}")
print(f"Time taken: {elapsed_time} seconds")
