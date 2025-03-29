import requests
from bs4 import BeautifulSoup
from logger import logger

def extract_p_tags(url):
    """Fetch and extract all <p> text from a given URL."""
    try:
        logger.info(f"Fetching content from URL: {url}")
        
        if not url or not isinstance(url, str):
            logger.error(f"Invalid URL provided: {url}")
            logger.warning("Returning empty string due to invalid URL")
            return ""
            
        logger.debug(f"Setting up request headers for URL: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            logger.debug(f"Sending HTTP request to: {url}")
            page = requests.get(url, headers=headers, timeout=30)
            logger.info(f"Received response with status code: {page.status_code}")
            
            if page.status_code != 200:
                logger.warning(f"Non-200 status code ({page.status_code}) from {url}")
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out for URL: {url}")
            return ""
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for URL: {url}")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return ""
        
        try:
            logger.debug(f"Parsing HTML content from {url}")
            soup = BeautifulSoup(page.text, 'html.parser')
            
            logger.debug(f"Extracting <p> tags from {url}")
            p_tags = soup.find_all('p')
            logger.info(f"Found {len(p_tags)} paragraph tags in {url}")
            
            paragraphs = " ".join(p.get_text() for p in p_tags)
            
            logger.info(f"Successfully extracted {len(paragraphs)} characters from {url}")
            return paragraphs
        except Exception as e:
            logger.error(f"HTML parsing error for {url}: {str(e)}")
            # Return whatever content we might have already
            return page.text if hasattr(page, 'text') else ""
            
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {str(e)}")
        logger.debug(f"Stack trace for error on {url}", exc_info=True)
        return ""