from app.config import MONGODB_URI
import pyodbc

print("Trying Connecting to SQL Server")

def get_db_connection():
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=LAPTOP-1CCOFVJE\\MSSQLSERVER1;"
        "Database=db_jansamvaad;"
        "Trusted_Connection=yes;"
    )
    connection = None
    try:
        connection = pyodbc.connect(connection_str, autocommit=True)
        print("Connected to SQL Server successfully.")
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
    return connection

def test_db_connection():
    connection = get_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            print("Query executed successfully, connection is working.")
        except Exception as e:
            print(f"Error running test query: {e}")
        finally:
            cursor.close()
            connection.close()

test_db_connection()