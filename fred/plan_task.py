from .config import config, APIKeyNotFoundError
import instructor
from openai import OpenAI
from typing import List, Union, Dict, Any
from .models import DAG, SearchNode, CodeNode, DisplayNode, DAGNode
import time
from collections import deque

try:
    client = instructor.from_openai(OpenAI(api_key=config.get_api_key("OPENAI_API_KEY")))
except APIKeyNotFoundError as e:
    print("API KEY Not Found!")
except Exception as e:
    print(e)

prompt = '''
You are an expert economist AI assistant specializing in the FRED (Federal Reserve Economic Data) database. Your task is to generate a Directed Acyclic Graph (DAG) of tasks to gather, analyze, and display data for answering user queries about economic topics.

Given a user query, your job is to:
1. Analyze the query to identify the main economic topics and indicators involved.
2. Generate a DAG of tasks, where each task is a node in the graph.
3. Use three types of nodes:
   a. SearchNode: for searching FRED series (query parameter required)
   b. CodeNode: for writing analysis code (code parameter required, must depend on at least one SearchNode)
   c. DisplayNode: for displaying results (display_type parameter required, must depend on at least one CodeNode)

Each node should have:
   - A unique ID
   - A list of dependencies (IDs of other nodes it depends on)
   - A task description
   - Specific parameters based on the node type

Ensure that:
1. The graph is acyclic (no circular dependencies)
2. Each task is specific and actionable
3. The overall graph, when executed, would provide a comprehensive answer to the user's query
4. Include a mix of search, code, and display nodes to fully address the query

Your output should be a list of DAG nodes, each with the appropriate structure based on its type.
'''

print("Ask your question")
query = input()
start = time.time()

dag: DAG = client.chat.completions.create(
    response_model=DAG,
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"The user query is: {query}"}
    ]
)

print(dag)

# Here you would implement the logic to execute the DAG
# This is a placeholder for where you'd process the DAG
def topological_sort(dag: DAG) -> List[DAGNode]:
    # Create a dictionary to store the in-degree of each node
    in_degree = {node.id: len(node.dependencies) for node in dag.nodes}
    
    # Create a dictionary to store the nodes by their IDs for easy lookup
    nodes_by_id = {node.id: node for node in dag.nodes}
    
    # Create a queue of nodes with no dependencies
    queue = deque([node for node in dag.nodes if len(node.dependencies) == 0])
    
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Decrease the in-degree of all nodes that depend on this node
        for other_node in dag.nodes:
            if node.id in other_node.dependencies:
                in_degree[other_node.id] -= 1
                if in_degree[other_node.id] == 0:
                    queue.append(other_node)
    
    if len(result) != len(dag.nodes):
        raise ValueError("The graph contains a cycle")
    
    return result

def execute_dag(dag: DAG):
    sorted_nodes = topological_sort(dag)
    node_outputs: Dict[str, Any] = {}

    for node in sorted_nodes:
        print(f"Executing node: {node.id}")
        
        # Gather inputs from dependencies
        inputs = {dep: node_outputs[dep] for dep in node.dependencies}
        
        if isinstance(node, SearchNode):
            # Implement search logic
            print(f"Searching for: {node.query}")
            # node_outputs[node.id] = search_function(node.query)
        elif isinstance(node, CodeNode):
            # Implement code execution logic
            print(f"Executing code: {node.code}")
            # node_outputs[node.id] = execute_code(node.code, inputs)
        elif isinstance(node, DisplayNode):
            # Implement display logic
            print(f"Displaying results using: {node.display_type}")
            # node_outputs[node.id] = create_display(node.display_type, inputs)
        
        # For now, we'll use a placeholder output
        node_outputs[node.id] = f"Placeholder output for {node.id}"
        
        # Update node output
        node.output = node_outputs[node.id]

print("DAG structure:")
print(dag)

print("\nExecuting DAG:")
execute_dag(dag)

print(f"\n\n\n. The time taken is {time.time() - start} seconds")
