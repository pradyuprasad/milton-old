import chromadb
import sqlite3
from typing import List, Dict
import os

print("Imported libraries")

# Connect to your SQLite database
DB_NAME = 'allData.db'
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    print("Connected to DB")
    return conn

# Initialize Chroma client with persistent storage
chroma_persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)

# Create or get the collection
collection = chroma_client.get_or_create_collection("fred-economic-series")

def get_series_with_tags() -> List[Dict[str, str]]:
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT s.fred_id, s.title, s.units, s.frequency, s.seasonal_adjustment, 
           s.last_updated, s.popularity, s.notes, GROUP_CONCAT(t.name, ', ') as tags
    FROM series s
    JOIN series_tags st ON s.id = st.series_id
    JOIN tags t ON st.tag_id = t.id
    GROUP BY s.id
    HAVING COUNT(t.id) > 0
    ORDER BY s.popularity DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    series_list = []
    for row in rows:
        series_list.append({
            'fred_id': row[0],
            'title': row[1],
            'units': row[2],
            'frequency': row[3],
            'seasonal_adjustment': row[4],
            'last_updated': row[5],
            'popularity': row[6],
            'notes': row[7],
            'tags': row[8]
        })
    
    conn.close()
    return series_list

def populate_chroma_db():
    series_list = get_series_with_tags()
    
    documents = []
    metadatas = []
    ids = []
    
    for series in series_list:
        # Combine all relevant fields into one document
        document = f"{series['title']} {series['tags']} {series['units']} {series['frequency']} {series['seasonal_adjustment']} {series['notes']}"
        document = document.lower()  # Normalize to lowercase
        documents.append(document)
        
        metadatas.append({
            'fred_id': series['fred_id'],
            'title': series['title'],
            'units': series['units'],
            'frequency': series['frequency'],
            'seasonal_adjustment': series['seasonal_adjustment'],
            'last_updated': series['last_updated'],
            'popularity': series['popularity'],
            'tags': series['tags']
        })
        ids.append(series['fred_id'])
    
    # Add to Chroma in batches to handle potential large datasets
    batch_size = 10
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )

if __name__ == "__main__":
    # Check if the collection is empty
    if collection.count() == 0:
        print("Chroma database is empty. Starting to populate...")
        populate_chroma_db()
        print("Chroma database population complete.")
    else:
        print("Chroma database already populated.")
    
    print(f"Total documents in Chroma: {collection.count()}")