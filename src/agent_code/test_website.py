import requests
import time

url = 'https://sgdataproject-microservice.onrender.com'

seconds_elapsed = 0

while True:
    try:
        start_time = time.time()  # Record the start time before making the request
        response = requests.get(url)
        end_time = time.time()  # Record the end time after getting the response
        if response.status_code == 200:
            print(f"Response received in {end_time - start_time:.2f} seconds.")
            break
    except requests.exceptions.RequestException as e:
        print(f"No response yet. Elapsed time: {seconds_elapsed} seconds.")
    
    time.sleep(5)
    seconds_elapsed += 5

