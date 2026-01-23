import requests
import re
import os
import json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def clean_html(text):
    """Remove HTML tags and entities"""
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def search_google(query, api_key=None, cx=None, max_results=5):

    results = []
    
    # Use environment variables or passed parameters
    api_key = api_key or os.environ.get('GOOGLE_API_KEY')
    cx = cx or os.environ.get('GOOGLE_CX')
    
    if not api_key or not cx:
        return results
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": min(max_results, 10)
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", "")
                results.append({
                    "snippet": snippet,
                    "url": item.get("link", ""),
                    "title": item.get("title", "")
                })
    except Exception as e:
        print(f"Google search error: {e}")
    
    return results

def search_wikipedia(query, max_results=5):
    """Search Wikipedia for content - with better error handling"""
    results = []
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": max_results
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, params=params, timeout=8, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            
            for item in search_results[:max_results]:
                snippet = clean_html(item.get("snippet", ""))
                if snippet and len(snippet) > 20:  # Only include meaningful snippets
                    title = item.get('title', '')
                    results.append({
                        "snippet": snippet,
                        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        "title": title,
                        "source": "wikipedia"
                    })
    except Exception as e:
        print(f"Wikipedia search error: {e}")

    return results

def search_bing(query, max_results=5):
    """
    Search using Bing (no API key required)
    More reliable than DuckDuckGo for plagiarism detection
    """
    results = []
    
    # Using Bing search via web scraping
    url = "https://www.bing.com/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    params = {
        'q': query,
        'count': max_results
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find search result items
            for item in soup.find_all('div', class_='b_algo')[:max_results]:
                try:
                    title_elem = item.find('h2')
                    snippet_elem = item.find('p')
                    link_elem = item.find('a')
                    
                    if title_elem and snippet_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        url_found = link_elem.get('href', '')
                        
                        if snippet and len(snippet) > 20 and url_found:
                            results.append({
                                "snippet": clean_html(snippet),
                                "url": url_found,
                                "title": title,
                                "source": "bing"
                            })
                except Exception as e:
                    continue
    except Exception as e:
        print(f"Bing search error: {e}")
    
    return results

def search_duckduckgo(query, max_results=5):
    """Search using DuckDuckGo (no API key required)"""
    results = []
    url = "https://api.duckduckgo.com/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    params = {
        "q": query,
        "format": "json",
        "no_html": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=8, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Get abstract if available
            abstract = data.get("AbstractText", "")
            if abstract and len(abstract) > 20:
                results.append({
                    "snippet": abstract,
                    "url": data.get("AbstractURL", ""),
                    "title": data.get("Heading", ""),
                    "source": "duckduckgo"
                })
            
            # Get related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    text = topic.get("Text", "")
                    if len(text) > 20:
                        results.append({
                            "snippet": text,
                            "url": topic.get("FirstURL", ""),
                            "title": topic.get("Text", "")[:50],
                            "source": "duckduckgo"
                        })
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
    
    return results

def search_web(query, max_results=5, use_google=False):
    """
    Search the web for plagiarism detection
    Combines multiple search sources for better coverage
    Priority: Bing (most reliable) > Wikipedia > DuckDuckGo > Google
    """
    all_results = []
    
    # Primary search: Bing (most reliable for plagiarism detection)
    print(f"Searching web for: '{query[:50]}...'")
    bing_results = search_bing(query, max_results=max_results)
    all_results.extend(bing_results)
    
    # Secondary search: Wikipedia (reliable academic sources)
    if len(all_results) < max_results:
        wiki_results = search_wikipedia(query, max_results=max_results)
        all_results.extend(wiki_results)
    
    # Tertiary search: DuckDuckGo
    if len(all_results) < max_results:
        ddg_results = search_duckduckgo(query, max_results=max_results)
        all_results.extend(ddg_results)
    
    # Optional: Google Custom Search if enabled and API key provided
    if use_google and len(all_results) < max_results:
        google_results = search_google(query, max_results=max_results)
        all_results.extend(google_results)
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "").lower()
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    # Return results, ensuring we have content
    final_results = unique_results[:max_results * 2]
    print(f"Found {len(final_results)} web results")
    return final_results

