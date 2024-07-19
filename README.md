This is my project to automatically analyse Singapore's economic data using LLMs. The basic idea is simple: type in a query, and the machine does everything for you and gives you an answer with a chart. You can ask a

# Usage
You can view the project at this link [here](https://github.com/pradyuprasad/EconDataGPTBackend/blob/main/images/example.jpg?raw=true). Alternatively, you can download it and run the backend by doing

```
export PORT=10000
uvicorn src.microservice.main:app --host 0.0.0.0 --port $PORT
```

# Example screenshots
![image](https://github.com/user-attachments/assets/c958e92d-25dd-4219-a7f6-f42760607ddc)

# How it works
There are four parts to this  
1. Data download
2. AI agent code
3. Running the microservice 
4. Rendering the frontend (in progress)

## Data download
All of the code in this is in the folder ```src/download```.  

