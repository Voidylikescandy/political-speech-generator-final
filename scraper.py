import requests
from bs4 import BeautifulSoup
from logger import logger

def extract_p_tags(url):
    """Fetch and extract all <p> text from a given URL."""
    try:
        logger.info(f"Fetching content from URL: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get(url, headers=headers, timeout=5)
        
        soup = BeautifulSoup(page.text, 'html.parser')
        paragraphs = " ".join(p.get_text() for p in soup.find_all('p'))
        
        logger.info(f"Successfully extracted {len(paragraphs)} characters from {url}")
        return paragraphs
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {str(e)}")
        # print(f"Error fetching {url}: {str(e)}")
        return ""