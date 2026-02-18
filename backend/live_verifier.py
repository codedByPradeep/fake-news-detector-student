from duckduckgo_search import DDGS
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# List of domains generally considered reliable
RELIABLE_SOURCES = {
    # Global Major
    "reuters.com", "apnews.com", "bbc.com", "npr.org", "pbs.org", "nytimes.com", 
    "washingtonpost.com", "wsj.com", "bloomberg.com", "cnn.com", "nbcnews.com", 
    "abcnews.go.com", "cbsnews.com", "usatoday.com", "theguardian.com", "dw.com",
    "euronews.com", "aljazeera.com", 
    

    # Tech / Science
    "theverge.com", "engadget.com", "cnet.com", "mashable.com", "techcrunch.com", 
    "wired.com", "arstechnica.com", "scientificamerican.com", "popsci.com",
    
    # Encyclopedias & General Reference (Crucial for historical/factual queries)
    "wikipedia.org", "britannica.com", "history.com", "biography.com", "snopes.com",
    "politifact.com", "factcheck.org", "whitehouse.gov", "nasa.gov", "un.org", "who.int",
    
    # More Global / US News
    "foxnews.com", "usnews.com", "time.com", "politico.com", "businessinsider.com",
    "slate.com", "vox.com", "vice.com", "huffpost.com", "msn.com", "yahoo.com",
    "telegraph.co.uk", "independent.co.uk", "standard.co.uk", "dailymail.co.uk",
    "nypost.com", "latimes.com", "chicagotribune.com", "boston.com", "sfgate.com",
    
    # Indian News & Entertainment (Crucial for user's context)
    "hindustantimes.com", "timesofindia.indiatimes.com", "ndtv.com", "indianexpress.com", 
    "thehindu.com", "livemint.com", "moneycontrol.com", "toi.in", "firstpost.com",
    "news18.com", "indiatoday.in", "zeenews.india.com", "dnaindia.com", "tellychakkar.com",
    "pinkvilla.com", "bollywoodhungama.com", "koimoi.com", "filmfare.com", "ani_news.in"
}

def verify_news_online(query: str, num_results: int = 10) -> Dict:
    """
    Searches specialized news queries on DuckDuckGo and checks if reliable sources are reporting it.
    Returns:
        - verification_status: "VERIFIED_REAL", "Likely_FAKE", "UNVERIFIED"
        - sources: List of URLs found
        - reliable_match_count: Number of reliable sources found
    """
    if not query or len(query.split()) < 3:
        return {"status": "UNVERIFIED", "sources": [], "message": "Query too short for verification"}
        
    logger.info(f"Verifying online with DuckDuckGo: {query}")
    
    found_sources = []
    reliable_count = 0
    reliable_matches = []
    
    try:
        results = []
        with DDGS() as ddgs:
            # Try to search for news specifically first
            # We fetch slightly more results to filter reliable ones
            search_results = list(ddgs.news(keywords=query, region="wt-wt", safesearch="off", max_results=num_results))
            
            # If news search returns nothing, fall back to general text search
            if not search_results:
                 logger.info("News search empty, trying general text search...")
                 search_results = list(ddgs.text(keywords=query, region="wt-wt", safesearch="off", max_results=num_results))

            for result in search_results:
                # DuckDuckGo returns keys: 'title', 'body', 'url', 'source', 'date'
                url = result.get('url') or result.get('href', '')
                title = result.get('title', '')
                source_name = result.get('source', '')
                
                if not url:
                    continue

                # Simple domain extraction
                if "//" in url:
                    domain = url.split("//")[-1].split("/")[0].replace("www.", "")
                else:
                    domain = url.split("/")[0]
                
                # Check for reliable source match
                is_reliable = any(source in domain for source in RELIABLE_SOURCES)
                
                # Also check if the source name from DDG itself is reliable (sometimes domain parsing fails)
                if not is_reliable and source_name:
                    source_clean = source_name.lower().replace(" ", "")
                    # Heuristic check
                    is_reliable = any(s.replace(".com","").replace(".org","") in source_clean for s in RELIABLE_SOURCES)

                source_entry = {
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "is_reliable": is_reliable,
                    "source": source_name
                }
                found_sources.append(source_entry)
                
                if is_reliable:
                    reliable_count += 1
                    reliable_matches.append(domain)
                    
    except Exception as e:
        logger.error(f"DuckDuckGo Search failed: {e}")
        return {"status": "ERROR", "sources": [], "message": "Live verification failed (Connection/Limit)"}


    # Logic to determine status
    status = "UNVERIFIED"
    message = "No clear news confirmation found."
    
    if reliable_count >= 1:
        status = "VERIFIED_REAL"
        sources_str = ", ".join(reliable_matches[:3])
        message = f"Verified by: {sources_str}"
    elif reliable_count == 0 and len(found_sources) >= 2:
        # If we found at least 2 sources, even if not in our rigorous 'reliable list',
        # it is highly unlikely to be purely AI-generated fake news (which typically has 0 results).
        # We downgrade detection to UNKNOWN/UNVERIFIED, but provide the sources.
        status = "UNVERIFIED"
        message = f"Found mentions on {len(found_sources)} sites (e.g., {found_sources[0]['domain']}), but not verified by major outlets."
    else:
        # ZERO or very few results found
        status = "UNVERIFIED"
        message = "No matching search results found online."

    return {
        "status": status,
        "sources": found_sources,
        "reliable_count": reliable_count,
        "message": message
    }

if __name__ == "__main__":
    # Self-test when run directly
    print("Running self-test...")
    test_query = "Donald Trump won the 2016 US Election"
    result = verify_news_online(test_query)
    print(f"Test 1 ({test_query}): {result['status']}")
    print(f"Message: {result['message']}")
    
    test_query_2 = "Rajat Dalal is in the 50 show"
    result_2 = verify_news_online(test_query_2)
    print(f"Test 2 ({test_query_2}): {result_2['status']}")
    print(f"Message: {result_2['message']}")
