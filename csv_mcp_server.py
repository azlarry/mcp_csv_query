# to start:  python csv_mcp_server.py --server_type=sse

import os
import pandas as pd
import sqlite3
import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('mcp-server-demo')

DB_FILE_PATH = "wr.db"


def csv_to_sqlite_pandas(csv_file_path: str, db_file_path: str, table_name: str):
    """
    Using pandas for more advanced data type inference
    """
    # Read CSV with pandas
    df = pd.read_csv(csv_file_path)
    
    df["Season"] = "2025" # source data does not specify the season
    df["Week"] = "1" # source data does not specify the week

    # Connect to SQLite database
    conn = sqlite3.connect(db_file_path)
    
    # Write DataFrame to SQLite table
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Close connection
    conn.close()
    print(f"Successfully created SQLite database '{db_file_path}' with table '{table_name}' using pandas")


def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    return conn, cursor


@mcp.tool()
def read_data(query: str = "SELECT * FROM wr_data") -> list:
    """Read data from the wide receiver table using a SQL SELECT query.

    Args:
        query (str, optional): SQL SELECT query. Defaults to "SELECT * FROM wr_data".
            Examples:
            - "SELECT * FROM wr_data"
            - "SELECT PlayerName, ReceivingYDS, ReceivingTD FROM wr_data WHERE Team='NE'"
            - "SELECT * FROM wr_data ORDER BY TotalPoints DESC"
    
    Returns:
        list: List of tuples containing the query results.  Each tuple represents a single NFL wide receiver.
    
    Example:
        >>> read_data("SELECT PlayerName, Targets FROM wr_data WHERE Targets > 15.0")
        [('Marquise Brown', '16.0')]
    """
    conn, cursor = init_db()
    try:
        print(f"read_data executing query: {query}")
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    
    try:
        print("🚀 Starting server... ")

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--server_type", type=str, default="sse", choices=["sse", "stdio"]
        )

        if os.path.exists(DB_FILE_PATH):
            print(f"File '{DB_FILE_PATH}' exists -- skipping database creation")
        else:
            csv_to_sqlite_pandas('WR.csv', 'wr.db', 'wr_data')

        args = parser.parse_args()
        mcp.run(args.server_type)
    
    except KeyboardInterrupt:
        print("🛑 Shutting down server... ")

    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("👋 Goodbye!")
