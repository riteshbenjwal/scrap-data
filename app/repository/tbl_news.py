import pyodbc
from app.db.database import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def insert_search_results(search_results: list):
    if not search_results:
        logger.info("No search results to insert.")
        return
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = '''INSERT INTO dbo.tbl_news (url, author, title, description, published_at, leader_name, category) 
                   VALUES (?, ?, ?, ?, ?, ?,?);'''
        values_to_insert = [
            (
                result.get("url"),
                result.get("author"),
                result.get("title"),
                result.get("description"),
                result.get("published_at"),
                result.get("leader_name"),
                result.get("category")

            )
            for result in search_results
        ]

        cursor.executemany(query, values_to_insert)
        db.commit()
        logging.info("Successfully inserted article: %s")
    except pyodbc.Error as e:
        if db is not None:
            db.rollback()
        logger.error("Database error: %s", e)
        logger.debug("Failed query: %s", query)
        logger.debug("With values: %s", values_to_insert)
    except KeyError as e:
        logger.error("Missing expected article_data key: %s", e)
        logger.debug("Article data: %s", values_to_insert)
    except Exception as e:
        if db is not None:
            db.rollback()
        logger.error("Unexpected error: %s", e)
        logger.debug("Article data: %s", values_to_insert)
    finally:
        if db is not None:
            db.close()
