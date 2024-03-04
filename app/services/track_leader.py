from app.repository.tbl_track_leader import insert_leader_track_data
from app.services.google_search import search_google
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_track_leader(leader_data):
    try:
        if not isinstance(leader_data,dict):
            leader_data=leader_data.dict()

        insert_result = insert_leader_track_data(leader_data)

        leader_name = leader_data.get("leader_name")

        if not leader_name:
            logger.error("leader_name is required")
            return

        logger.info("Successfully inserted leader data: %s", leader_name)

        if leader_name:
            print("Calling Search Google Service")
            search_results = await search_google(leader_name, 1)

            return {
                "insert_result": insert_result,
                "search_results": search_results
            }
        else:
            raise ValueError("The leader_name field is missing from the leader data.")
    except ValueError as ve:
        logger.error("Value error: %s", ve)
        raise
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise
