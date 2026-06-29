from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

BLOCKED_DOMAINS = [
    "kresearch.com", "mordorintelligence.com",
    "grandviewresearch.com", "marketsandmarkets.com",
]

def research_agent(query_plan: dict) -> dict:

    # Get everything from query plan
    original_query    = query_plan.get("original_query", "")
    search_queries    = query_plan.get("search_queries", [])
    countries         = query_plan.get("countries", [])
    sector            = query_plan.get("sector", "")
    preferred_sources = query_plan.get("preferred_sources", []) 

    print(f"🔍 Research Agent started...")
    print(f"   Countries:         {countries}")
    print(f"   Sector:            {sector}")
    print(f"   Preferred sources: {preferred_sources}")        

    # ── PRIORITY SEARCHES ────────────────────────────────
    # Build extra searches targeting preferred sources directly
    priority_searches = []
    for source in preferred_sources:
        priority_searches.append(
            f"{original_query} site:{source}"
        )

    # Combine — priority searches first, then regular searches
    all_searches = priority_searches + search_queries           

    print(f"   Priority searches: {len(priority_searches)}")    
    print(f"   Regular searches:  {len(search_queries)}")       
    print(f"   Total searches:    {len(all_searches)}")         

    results   = []
    seen_urls = set()

    for search_query in all_searches:                       
        try:
            response = client.search(
                query=search_query,
                max_results=4,
                search_depth="advanced"
            )
            for result in response["results"]:

                # Skip blocked domains
                if any(d in result["url"] for d in BLOCKED_DOMAINS):
                    continue

                # Skip duplicates
                if result["url"] in seen_urls:
                    continue

                seen_urls.add(result["url"])
                results.append({
                    "title":   result["title"],
                    "url":     result["url"],
                    "content": result["content"][:800]
                })

        except Exception as e:
            print(f"   ⚠️ Search failed: {e}")
            continue

    print(f"   📄 Unique sources found: {len(results)}")

    return {
        "original_query": original_query,
        "query_plan":     query_plan,
        "results":        results
    }