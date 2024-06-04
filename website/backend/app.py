from typing import Optional

from fastapi import FastAPI

from ...ai_tools.database_selector import write_dataset_picking_instructions, write_SQL_query

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/data_selector")
def get_dataset():
    return None