import json
import http.client
import time
from scraper import extract_p_tags
from config import SERPER_API_KEY, SERPER_API_HOST

def serper_search(query, num_results=1, pages=1):
    conn = http.client.HTTPSConnection(SERPER_API_HOST)
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": query, "gl": "in", "num": num_results, "page": pages, "type": "search"})

    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    return json.loads(res.read().decode("utf-8"))

def fetch_additional_results(query, min_results=4):
    for attempt in range(1, 5):
        print(f"Trying {attempt}/5")
        data = serper_search(query, num_results=min_results)
        if data.get("organic"):
            break
        time.sleep(1)

    results = {}
    for item in data.get("organic", []):
        link = item.get("link", "")
        if link:
            extracted_text = extract_p_tags(link)
            if extracted_text:
                results[link] = extracted_text

    return results
