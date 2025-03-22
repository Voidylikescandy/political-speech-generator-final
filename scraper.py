import requests
from bs4 import BeautifulSoup

def extract_p_tags(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(page.text, 'html.parser')
        return " ".join(p.get_text() for p in soup.find_all('p'))
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""
