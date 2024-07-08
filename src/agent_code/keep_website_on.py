import requests
import time

url = 'https://sgdataproject-microservice.onrender.com'

try:
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Response received: {response.text}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
        
        time.sleep(5)  # Wait for 5 seconds before making the next request

except KeyboardInterrupt:
    print("\nScript interrupted by user.")

