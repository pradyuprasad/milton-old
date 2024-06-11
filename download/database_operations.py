import json
import uuid
import libsql_experimental as libsql # type: ignore
from dotenv import load_dotenv, find_dotenv
import threading
import os
from .classes import DatabaseRow
from typing import Optional, Type
import sys

# Load environment variables
env_path = find_dotenv()
load_dotenv(env_path)
print(env_path)
for key, value in os.environ.items():
    print(f"{key}: {value}")


DB_URL = os.getenv("TURSO_DB_URL")
DB_TOKEN = os.getenv("TURSO_DB_TOKEN")


if not DB_URL or not DB_TOKEN:
    raise ValueError("Database URL or Token is not set in the environment variables.")

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _lock: threading.Lock = threading.Lock()
    _conn: Optional[libsql.Connection] = None

    def __new__(cls: Type['DatabaseConnection']) -> 'DatabaseConnection':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
                    cls._instance._conn = cls._initialize_connection()
        return cls._instance

    @classmethod
    def _initialize_connection(cls) -> Optional[libsql.Connection]:
        try:
            conn = libsql.connect("dataset-metadata", sync_url=DB_URL, auth_token=DB_TOKEN, sync_interval=60)
            conn.sync()
            print("Database connection established and synced.")
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    def get_connection(self) -> Optional[libsql.Connection]:
        return self._conn

def make_dataset_table() -> None:
    try:
        # Obtain database connection
        DB = DatabaseConnection().get_connection()
        if DB is None:
            raise ValueError("Failed to connect to the database.")
        
        # SQL statement for creating the table with the specified schema
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS datasets (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            AggregationId TEXT NOT NULL,
            AggregationOfficialName TEXT NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('monthly', 'quarterly')),
            footnote TEXT,
            unitOfMeasure TEXT NOT NULL,
            startDate DATE NOT NULL,
            endDate DATE NOT NULL,
            ElementName TEXT NOT NULL,
            filePath TEXT NOT NULL,
            dataType TEXT NOT NULL CHECK (dataType IN ('REAL_GDP', 'Nominal_GDP', 'Unemployment', 'Consumer_Price_Index')),
            level TEXT NOT NULL CHECK (level IN ('TotalEconomy', 'SuperSector', 'Sector', 'SubSector')),
            parent TEXT
        )
        '''
        
        # Execute the SQL statement to create the table
        DB.execute(create_table_sql)
        DB.commit()  # Commit changes to the database
        print("Table created successfully.")
        
    except Exception as e:
        print(f"Error creating table: {e}")

def drop_datasets() -> None:
    try:
        DB = DatabaseConnection().get_connection()
        if DB is None:
            raise ValueError("Failed to connect to the database.")
        drop_table = '''
        DROP TABLE IF EXISTS datasets    
        '''
        DB.execute(drop_table)
        print("Table dropped successfully.")
    except Exception as e:
        print(f"Error dropping table: {e}")

def escape_single_quotes(value: str) -> str:
    """Escapes single quotes in a string for SQL statements."""
    return value.replace("'", "''")

def insert_database_row(row: DatabaseRow) -> None:
   
    try:
        print(DB_TOKEN)
        # Obtain database connection
        DB = DatabaseConnection().get_connection()
        if DB is None:
            raise ValueError("Failed to connect to the database.")

        #Formulate the SQL statement using direct string interpolation
        insert_sql = f'''
        REPLACE INTO datasets (
            AggregationId, AggregationOfficialName, frequency, footnote, unitOfMeasure,
            startDate, endDate, ElementName, filePath, dataType, level, parent
        ) VALUES (
            '{escape_single_quotes(row.AggregationId)}', '{escape_single_quotes(row.AggregationOfficialName)}', '{row.frequency}',
            '{escape_single_quotes(row.footnote)}', '{row.unitOfMeasure}', '{row.startDate}', '{row.endDate}',
            '{escape_single_quotes(row.ElementName)}', '{escape_single_quotes(row.filePath)}', '{row.dataType}', '{row.level}', 
            '{row.parent if row.parent is not None else "NULL"}'
        )
        '''

        # Execute the SQL statement
        DB.execute(insert_sql)
        DB.commit()  # Commit changes to the database
        DB.sync()
        print(f"Record {insert_sql} inserted successfully.")

    except Exception as e:
        print("Error for", insert_sql)
        print(f"Error inserting data: {e}")
        sys.exit(1)
        

if __name__ == "__main__":
    print()
    drop_datasets()
    make_dataset_table()
