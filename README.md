This is my project to automatically analyse Singapore's economic data using LLMs. The basic idea is simple: type in a query, and the machine does everything for you and gives you an answer with a chart. You can ask a

# Usage
You can view the project at this link [here](https://sgdataproject-frontend.onrender.com/). Alternatively, you can download it and run the backend by doing

```
export PORT=10000
uvicorn src.microservice.main:app --host 0.0.0.0 --port $PORT
```

# Example screenshots
[image](images/example.jpg)

# How it works
There are four parts to this  
1. Data download
2. AI agent code
3. Running the microservice 
4. Rendering the frontend (in progress)

## Data download
All of the code in this is in the folder ```src/download```.  

