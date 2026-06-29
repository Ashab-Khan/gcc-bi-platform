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

def analysis_agent(research_output: dict) -> dict:

    print(f"🧠 Analysis Agent started...")

    # Use new key names from research_agent
    original_query = research_output["original_query"]
    query_plan     = research_output["query_plan"]
    results        = research_output["results"]

    # Get dynamic fields from query_plan
    extract_fields = query_plan.get("extract_fields", ["name", "country", "product", "funding"])
    query_type     = query_plan.get("query_type", "startup_discovery")
    fields_str     = ", ".join(extract_fields)

    all_items  = []
    batch_size = 6

    for i in range(0, len(results), batch_size):

        batch = results[i:i + batch_size]
        print(f"   Processing batch {i//batch_size + 1} of {(len(results) + batch_size - 1)//batch_size}...")

        # Build text for this batch
        raw_text = ""
        for result in batch:
            raw_text += f"Title: {result['title']}\n"
            raw_text += f"Content: {result['content']}\n"
            raw_text += f"URL: {result['url']}\n\n"

        # Dynamic system message based on query_type
        system_message = SystemMessage(content=f"""
You are a business intelligence analyst specializing in GCC tech ecosystem.
GCC countries are: Saudi Arabia, UAE, Qatar, Bahrain, Kuwait, Oman.

Query Type: {query_type}
Extract these fields for each item found: {fields_str}

GENERAL RULES:
- Only extract real, specific entities
- Never include news headlines as entity names
- Never include generic terms like "GCC startups" or "MENA companies"
- Fill "Unknown" for any missing fields
- Return ONLY a valid JSON array
- If nothing found in this batch return []

RULES BY QUERY TYPE:

If query_type is "startup_discovery":
- Extract real startup and tech company names only
- Exclude government ministries, hospitals, global giants like Microsoft/Google
- Exclude VC funds and investors
- Product field must be specific, never just "tech startup"

If query_type is "funding_intelligence":
- Extract companies that received actual funding
- Include funding amount, round type (Seed/Series A etc), date, investor names
- Skip companies with no funding data

If query_type is "comparison":
- Extract metrics, statistics, and data points per country
- Focus on numbers, percentages, rankings

If query_type is "sector_report":
- Extract key insights, trends, statistics about the sector
- Include market size figures, adoption rates, key players

If query_type is "hiring_talent":
- Extract companies actively hiring
- Include role titles, locations, salary if mentioned

If query_type is "investor_research":
- Extract investor names, funds, accelerators
- Include portfolio companies and focus sectors
""")

        # Use original_query in human message
        human_message = HumanMessage(content=f"""
Original Query: {original_query}
Query Type: {query_type}

Web Data:
{raw_text}

Extract all relevant items based on the query type.
Return JSON array only. Each item must have these fields: {fields_str}
""")

        try:
            response     = llm.invoke([system_message, human_message])
            raw_response = response.content.strip()

            # Clean markdown code fences if present
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0]
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0]

            batch_items = json.loads(raw_response.strip())
            all_items.extend(batch_items)
            print(f"   ✅ Found {len(batch_items)} items in this batch")

        except Exception as e:
            print(f"   ⚠️ Batch failed: {e}")
            continue

   
    seen_names   = set()
    unique_items = []
    first_key    = extract_fields[0] if extract_fields else "name"

    for item in all_items:

        if query_type == "comparison":
            # For comparison use entity + metric combined as unique key
            identifier = f"{item.get('entity','')}_{item.get('metric','')}".lower().strip()

        elif query_type == "sector_report":
            # For sector report use insight trimmed to 50 chars
            identifier = str(item.get("insight", item.get("metric", ""))).lower()[:50].strip()

        else:
            # For everything else use first field
            identifier = str(item.get(first_key, "")).lower().strip()

        if identifier and identifier not in seen_names:
            seen_names.add(identifier)
            unique_items.append(item)

    print(f"✅ Total unique items found: {len(unique_items)}")

  
    return {
        "original_query": original_query,
        "query_plan":     query_plan,
        "items":          unique_items,
        "total":          len(unique_items)
    }