import urllib.parse
import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Any

def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search ArXiv for papers based on a text query.
    Returns a list of dicts with title, summary (abstract), and paper URL/id.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return [{"error": f"Failed to connect to ArXiv API (HTTP {response.status_code})"}]
        
        root = ET.fromstring(response.content)
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', namespaces):
            title = entry.find('atom:title', namespaces)
            summary = entry.find('atom:summary', namespaces)
            id_url = entry.find('atom:id', namespaces)
            
            title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown Title"
            summary_text = summary.text.strip().replace('\n', ' ') if summary is not None else "No abstract available"
            paper_id = id_url.text.strip() if id_url is not None else ""
            
            results.append({
                "title": title_text,
                "summary": summary_text,
                "url": paper_id
            })
            
        if not results:
            return [{"info": "No papers found matching the query."}]
            
        return results
    except Exception as e:
        return [{"error": f"An error occurred during ArXiv search: {str(e)}"}]

if __name__ == "__main__":
    # Test execution
    print(search_arxiv("prompt tuning", max_results=2))
