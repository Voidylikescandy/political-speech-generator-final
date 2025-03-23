import json
import http.client
import time
from scraper import extract_p_tags
from config import SERPER_API_KEY, SERPER_API_HOST

def serper_search(query, num_results=1, pages=1):
    """Fetches search results from Serper API."""
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

    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)

def fetch_additional_results(table, query, min_results=4):
    """Fetches additional results using Serper API if needed."""
    retries = 10
    data = {}

    for attempt in range(1, retries + 1):
        # print(f"Trying {attempt}/{retries}")
        data = serper_search(query, num_results=min_results)
        
        if data.get("organic"):
            break
        time.sleep(1)

    # print(f"Retrieved {len(data.get('organic', []))} results")
    
    # Dictionary to store link -> extracted text mapping
    results = {}
    
    for item in data.get("organic", []):
        link = item.get("link", "")
        if link:
            # Check if this source_id (URL) already exists in the database
            source_id = link
            try:
                # Check if the source_id exists using a where clause
                existing_records = table.search("").where(f"source_id = '{source_id}'").limit(1).to_pandas()
                if len(existing_records) > 0:
                    # print(f"Skipping {source_id} - already in database")
                    continue
            except Exception as e:
                # If there's an error (e.g., column doesn't exist yet), proceed with extraction
                # print(f"Error checking for existing source_id: {e}")
                pass
            
            extracted_text = extract_p_tags(link)
            if extracted_text:
                results[link] = extracted_text

    return results
