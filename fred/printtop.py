import sqlite3

# Connect to the database
DB_NAME = 'allData.db'

def connect_db():
    return sqlite3.connect(DB_NAME)

conn = connect_db()
cursor = conn.cursor()

# Query to fetch series IDs, titles, units, and tags in order of popularity
query = """
SELECT s.fred_id, s.title, s.units, GROUP_CONCAT(t.name, ', ') as tags
FROM series s
JOIN series_tags st ON s.id = st.series_id
JOIN tags t ON st.tag_id = t.id
GROUP BY s.id
HAVING COUNT(t.id) > 0
ORDER BY s.popularity DESC
"""

cursor.execute(query)
rows = cursor.fetchall()

# Initialize counter
with_tags_count = 0

# Print the series IDs, titles, units, and tags, and count them
for row in rows:
    series_id, title, units, tags = row
    with_tags_count += 1
    print(f"count: {with_tags_count}")
    print(f"ID: {series_id}")
    print(f"Title: {title}")
    print(f"Units: {units}")
    print(f"Tags: {tags}")
    print("---")  # Separator for readability

# Print the count
print(f"\nTotal series with tags: {with_tags_count}")

# Close the database connection
conn.close()