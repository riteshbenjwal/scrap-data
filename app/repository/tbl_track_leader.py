import pyodbc
from app.db.database import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_leader_track_data(leader_data: dict):
    if not leader_data:
        logger.info("No leader data to insert.")
        return

    db = None
    values_to_insert = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = '''INSERT INTO dbo.tbl_track_leader (user_id, leader_name, keywords, hsh_tag, twitter_handle, 
                   facebook_id, instagram_id, frequency_update) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''
        values_to_insert = (
            leader_data.get("user_id"),
            leader_data["leader_name"],
            leader_data.get("keywords"),
            leader_data.get("hash_tag"),
            leader_data.get("twitter_handle"),
            leader_data.get("facebook_id"),
            leader_data.get("instagram_id"),
            leader_data.get("frequency_update")
        )

        cursor.execute(query, values_to_insert)
        db.commit()
        logger.info("Successfully inserted leader data: %s", leader_data["leader_name"])
    except pyodbc.Error as e:
        if db is not None:
            db.rollback()
        logger.error("Database error: %s", e)
        logger.debug("Failed query: %s", query)
        # Check if values_to_insert was defined
        if values_to_insert:
            logger.debug("With values: %s", values_to_insert)
    except KeyError as e:
        logger.error("Missing expected leader_data key: %s", e)
        # Check if values_to_insert was defined
        if values_to_insert:
            logger.debug("Leader data: %s", values_to_insert)
    except Exception as e:
        if db is not None:
            db.rollback()
        logger.error("Unexpected error: %s", e)
        # Check if values_to_insert was defined
        if values_to_insert:
            logger.debug("Leader data: %s", values_to_insert)
    finally:
        if db is not None:
            db.close()
