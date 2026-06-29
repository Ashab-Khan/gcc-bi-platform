from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# GCC context — injected into every query analysis
GCC_CONTEXT = {
    "Saudi Arabia": {
        "cities":   ["Riyadh", "Jeddah", "NEOM", "Dhahran"],
        "programs": ["Vision 2030", "PIF", "SDAIA", "STV", "NEOM"],
    },
    "UAE": {
        "cities":   ["Dubai", "Abu Dhabi", "Sharjah"],
        "programs": ["UAE AI Strategy", "Hub71", "ADIO", "DIFC"],
    },
    "Qatar": {
        "cities":   ["Doha"],
        "programs": ["Qatar Vision 2030", "QFC", "QSTP"],
    },
    "Bahrain": {
        "cities":   ["Manama"],
        "programs": ["Bahrain Vision 2030", "Tamkeen", "Bahrain FinTech Bay"],
    },
    "Kuwait": {
        "cities":   ["Kuwait City"],
        "programs": ["Kuwait Vision 2035", "KFAS"],
    },
    "Oman": {
        "cities":   ["Muscat"],
        "programs": ["Oman Vision 2040", "Madayn", "Knowledge Oasis Muscat"],
    }
}

# Best sources per query type
GCC_SOURCES = {
    "startup_discovery":    ["magnitt.com", "wamda.com", "zawya.com"],
    "funding_intelligence": ["magnitt.com", "arabianbusiness.com", "zawya.com"],
    "comparison":           ["magnitt.com", "wamda.com", "arabianbusiness.com"],
    "sector_report":        ["wamda.com", "zawya.com", "gulfnews.com"],
    "hiring_talent":        ["bayt.com", "gulftalent.com", "linkedin.com"],
    "investor_research":    ["magnitt.com", "saudivc.com", "hub71.com"],
}

def query_agent(user_query: str) -> dict:

    print(f"🧩 Query Agent started...")
    print(f"   Analyzing: '{user_query}'")

    system_message = SystemMessage(content=f"""
You are a GCC Business Intelligence query analyzer.
GCC countries are: Saudi Arabia, UAE, Qatar, Bahrain, Kuwait, Oman.

GCC Context you must use:
{json.dumps(GCC_CONTEXT, indent=2)}

Analyze the user query and return a JSON object with these fields:

1. query_type: one of exactly:
   - "startup_discovery"    → finding companies or startups
   - "funding_intelligence" → funding rounds, investments, raised money
   - "comparison"           → comparing two or more countries or sectors
   - "sector_report"        → overview or report of an industry
   - "hiring_talent"        → jobs, hiring, talent, recruitment
   - "investor_research"    → VCs, investors, funding bodies

2. countries: list of GCC countries relevant to this query
   - If query says "GCC" → include all 6 countries
   - If specific country mentioned → include only that one

3. sector: main industry focus
   - Examples: "AI", "healthcare", "fintech", "edtech", "general"

4. time_period: if mentioned
   - Examples: "2024", "this month", "Q1 2025", "recent"
   - If not mentioned → "recent"

5. search_queries: list of exactly 8 targeted web search queries
   - Must be specific to GCC/MENA context
   - Must cover different angles
   - Include country names, sector names, and relevant GCC programs

6. extract_fields: list of fields to extract based on query_type
   - startup_discovery:    ["name", "country", "city", "sector", "product", "funding", "founded", "source_url"]
   - funding_intelligence: ["company", "country", "amount", "round_type", "date", "investors", "source_url"]
   - comparison:           ["entity", "country", "metric", "value", "year", "source_url"]
   - sector_report:        ["insight", "metric", "value", "country", "source", "source_url"]
   - hiring_talent:        ["company", "role", "location", "salary", "requirements", "apply_url"]
   - investor_research:    ["name", "country", "focus_sectors", "portfolio_size", "notable_investments", "source_url"]

7. report_title: professional title for the final report
   - Example: "GCC AI Startup Intelligence Report — Healthcare Sector 2024"

Return ONLY a valid JSON object. No explanation. No markdown.
""")

    human_message = HumanMessage(content=f"""
User Query: {user_query}

Analyze and return the JSON object.
""")

    response = llm.invoke([system_message, human_message])
    raw      = response.content.strip()

    # Clean markdown
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]

    query_plan = json.loads(raw.strip())

    # Add original query to plan
    query_plan["original_query"] = user_query

   
    query_type = query_plan.get("query_type", "startup_discovery")
    query_plan["preferred_sources"] = GCC_SOURCES.get(query_type, [])

    print(f"   ✅ Type:      {query_plan['query_type']}")
    print(f"   ✅ Countries: {query_plan['countries']}")
    print(f"   ✅ Sector:    {query_plan['sector']}")
    print(f"   ✅ Searches:  {len(query_plan['search_queries'])} planned")
    print(f"   ✅ Sources:   {query_plan['preferred_sources']}")

    return query_plan