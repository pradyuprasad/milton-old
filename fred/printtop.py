import sqlite3

# Connect to the database
DB_NAME = 'allData.db'

def connect_db():
    return sqlite3.connect(DB_NAME)

conn = connect_db()
cursor = conn.cursor()

# Query to fetch series IDs, titles, and units with their tags in order of popularity
query = """
SELECT s.fred_id, s.title, s.units
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

# Print the series IDs, titles, and units, and count them
for row in rows:
    series_id, title, units = row
    with_tags_count += 1
    print(f"ID: {series_id}, Title: {title}, Units: {units}")

# Print the count
print(f"\nTotal series with tags: {with_tags_count}")

# Close the database connection
conn.close()
