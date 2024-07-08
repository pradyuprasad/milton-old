from transformers import pipeline  # type: ignore
import time
from typing import List, Any, Dict, Callable
from memory_profiler import profile  # type: ignore

@profile  # This decorator enables memory profiling for the load_model function.
def load_model() -> Callable[[str, List[str]], Dict[str, List[str]]]:
    start_time = time.time()
    classifier: Callable[[str, List[str]], Dict[str, List[str]]] = pipeline("zero-shot-classification", model="sileod/deberta-v3-small-tasksource-nli")
    print("--- %s seconds ---" % (time.time() - start_time))
    return classifier

classifier = load_model()

@profile  # This decorator is also applied here to monitor the memory usage during the classification.
def classify(query: str, labels: List[str]) -> Dict[str, List[str]]:
    output: Dict[str, List[str]] = classifier(query, labels)
    return output

print(classify("This is a happy day", ["happy", "sad"]))