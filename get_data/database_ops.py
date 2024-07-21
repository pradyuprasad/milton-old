import sqlite3

def create_tables():
    conn = sqlite3.connect('allData.db')
    c = conn.cursor()

    # Create categories table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fred_id INTEGER UNIQUE,
            name TEXT,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
    ''')

    # Create releases table
    c.execute('''
        CREATE TABLE IF NOT EXISTS releases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fred_id INTEGER UNIQUE,
            realtime_start TEXT,
            realtime_end TEXT,
            name TEXT,
            press_release BOOLEAN,
            link TEXT
        )
    ''')

    # Create series table
    c.execute('''
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fred_id TEXT UNIQUE,
            realtime_start TEXT,
            realtime_end TEXT,
            title TEXT,
            observation_start TEXT,
            observation_end TEXT,
            frequency TEXT,
            frequency_short TEXT,
            units TEXT,
            units_short TEXT,
            seasonal_adjustment TEXT,
            seasonal_adjustment_short TEXT,
            last_updated TEXT,
            popularity INTEGER,
            notes TEXT
        )
    ''')

    # Create tags table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fred_id INTEGER UNIQUE,
            name TEXT,
            group_id TEXT,
            notes TEXT,
            created TEXT,
            popularity INTEGER,
            series_count INTEGER
        )
    ''')

    # Create sources table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fred_id INTEGER UNIQUE,
            realtime_start TEXT,
            realtime_end TEXT,
            name TEXT,
            link TEXT
        )
    ''')

    # Create join tables for many-to-many relationships
    # Categories and Series
    c.execute('''
        CREATE TABLE IF NOT EXISTS category_series (
            category_id INTEGER,
            series_id INTEGER,
            PRIMARY KEY (category_id, series_id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (series_id) REFERENCES series(id)
        )
    ''')

    # Releases and Series
    c.execute('''
        CREATE TABLE IF NOT EXISTS release_series (
            release_id INTEGER,
            series_id INTEGER,
            PRIMARY KEY (release_id, series_id),
            FOREIGN KEY (release_id) REFERENCES releases(id),
            FOREIGN KEY (series_id) REFERENCES series(id)
        )
    ''')

    # Series and Tags
    c.execute('''
        CREATE TABLE IF NOT EXISTS series_tags (
            series_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (series_id, tag_id),
            FOREIGN KEY (series_id) REFERENCES series(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    # Categories and Tags
    c.execute('''
        CREATE TABLE IF NOT EXISTS category_tags (
            category_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (category_id, tag_id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    # Releases and Tags
    c.execute('''
        CREATE TABLE IF NOT EXISTS release_tags (
            release_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (release_id, tag_id),
            FOREIGN KEY (release_id) REFERENCES releases(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    # Releases and Sources
    c.execute('''
        CREATE TABLE IF NOT EXISTS release_sources (
            release_id INTEGER,
            source_id INTEGER,
            PRIMARY KEY (release_id, source_id),
            FOREIGN KEY (release_id) REFERENCES releases(id),
            FOREIGN KEY (source_id) REFERENCES sources(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
