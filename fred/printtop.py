import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('allData.db')
cursor = conn.cursor()

# Execute the query to get the top 100 by popularity in descending order
cursor.execute('''
    SELECT fred_id, title, popularity
    FROM series
    ORDER BY popularity DESC
    LIMIT 1000
''')

# Fetch the results
results = cursor.fetchall()

# Print the results
for row in results:
    print(f'fred_id: {row[0]}, title: {row[1]}, popularity: {row[2]}')

# Close the connection
conn.close()
