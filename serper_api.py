import json
import http.client
import time
from scraper import extract_p_tags
from config import SERPER_API_KEY, SERPER_API_HOST
from logger import logger

def serper_search(query, num_results=1, pages=1):
    """Fetches search results from Serper API."""
    try:
        logger.info(f"Searching Serper API for query: {query}")
        conn = http.client.HTTPSConnection(SERPER_API_HOST)
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "q": query,
            "gl": "in",
            "num": num_results,
            "page": pages,
            "type": "search"
        })

        logger.debug(f"Sending request to Serper API with payload: {payload}")
        conn.request("POST", "/search", payload, headers)
        
        logger.debug("Waiting for Serper API response")
        res = conn.getresponse()
        status = res.status
        logger.debug(f"Received response with status code: {status}")
        
        if status != 200:
            logger.error(f"Serper API returned non-200 status code: {status}")
            return {}
            
        data = res.read().decode("utf-8")
        logger.info(f"Received response from Serper API ({len(data)} bytes)")
        
        try:
            parsed_data = json.loads(data)
            logger.debug(f"Successfully parsed JSON response with {len(parsed_data.get('organic', []))} organic results")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {}
            
    except http.client.HTTPException as e:
        logger.error(f"HTTP error during Serper API request: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error in serper_search: {str(e)}")
        logger.debug("Stack trace for serper_search error", exc_info=True)
        return {}

def fetch_additional_results(table, query, min_results=4):
    """Fetches additional results using Serper API if needed."""
    try:
        retries = 10
        data = {}

        for attempt in range(1, retries + 1):
            logger.info(f"Attempt {attempt}/{retries} to fetch additional results")
            # print(f"Trying {attempt}/{retries}")
            data = serper_search(query, num_results=min_results)
            
            if data.get("organic"):
                logger.info("Successfully retrieved organic search results")
                break
            logger.warning(f"No organic results found in attempt {attempt}, retrying...")
            time.sleep(1)

        # print(f"Retrieved {len(data.get('organic', []))} results")
        result_count = len(data.get("organic", []))
        logger.info(f"Retrieved {result_count} results")
        
        if result_count == 0:
            logger.warning("No results found after all retry attempts")
            return {}

        # Dictionary to store link -> extracted text mapping
        results = {}
        
        for item in data.get("organic", []):
            try:
                link = item.get("link", "")
                if not link:
                    logger.warning("Skipping result with no link")
                    continue
                    
                # Check if this source_id (URL) already exists in the database
                source_id = link
                try:
                    # Check if the source_id exists using a where clause
                    logger.debug(f"Checking if {source_id} exists in database")
                    existing_records = table.search("").where(f"source_id = '{source_id}'").limit(1).to_pandas()
                    if len(existing_records) > 0:
                        logger.info(f"Skipping {source_id} - already in database")
                        # print(f"Skipping {source_id} - already in database")
                        continue
                except Exception as e:
                    # If there's an error (e.g., column doesn't exist yet), proceed with extraction
                    logger.warning(f"Error checking for existing source_id {source_id}: {e}")
                    # print(f"Error checking for existing source_id: {e}")
                    pass
                
                logger.info(f"Extracting text from {link}")
                extracted_text = extract_p_tags(link)
                if extracted_text:
                    logger.info(f"Successfully extracted {len(extracted_text)} characters from {source_id}")
                    results[link] = extracted_text
                else:
                    logger.warning(f"No text extracted from {link}")
            except Exception as e:
                logger.error(f"Error processing search result: {str(e)}")
                continue

        logger.info(f"Successfully extracted text from {len(results)} URLs")
        return results
    except Exception as e:
        logger.error(f"Unexpected error in fetch_additional_results: {str(e)}")
        logger.debug("Stack trace for fetch_additional_results error", exc_info=True)
        return {}
