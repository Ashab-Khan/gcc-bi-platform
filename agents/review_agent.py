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

def review_agent(analysis_output: dict) -> dict:

    print(f"🔎 Review Agent started...")

    original_query = analysis_output["original_query"]
    query_plan     = analysis_output["query_plan"]
    items          = analysis_output["items"]
    query_type     = query_plan.get("query_type", "startup_discovery")
    countries      = query_plan.get("countries", [])
    sector         = query_plan.get("sector", "")

    print(f"   Reviewing {len(items)} items...")

    # Process in batches to avoid token limits
    verified_items = []
    rejected_items = []
    batch_size     = 8

    for i in range(0, len(items), batch_size):

        batch = items[i:i + batch_size]
        print(f"   Reviewing batch {i//batch_size + 1} of {(len(items) + batch_size - 1)//batch_size}...")

        # Convert batch to clean text for review
        batch_text = json.dumps(batch, indent=2)

        system_message = SystemMessage(content=f"""
You are a strict quality control analyst for a GCC Business Intelligence platform.

Your job is to review extracted data and decide what to KEEP and what to REJECT.

Query Context:
- Original Query: {original_query}
- Query Type: {query_type}
- Target Countries: {', '.join(countries)}
- Sector Focus: {sector}

KEEP an item if:
- It is genuinely relevant to the query
- It is a real company or entity (not a news headline)
- It is based in or directly operating in the target countries
- It belongs to the target sector

REJECT an item if:
- It is not relevant to the query topic
- It is a global company with just a small office in the region
  (e.g. TechGropse, ELEKS, Tredence are Indian/Ukrainian companies)
- It is a government ministry (e.g. SDAIA unless query asks for it)
- It is a VC fund when query asks for startups
- It has almost no data (only name known, everything else Unknown)
  AND it does not seem like a notable company

For each item return a JSON object with:
- item: the original item data (unchanged)
- decision: "keep" or "reject"
- reason: one short sentence explaining why

Return ONLY a valid JSON array of these decision objects.
""")

        human_message = HumanMessage(content=f"""
Review these {len(batch)} items and decide keep or reject for each:

{batch_text}

Return JSON array with decision for each item.
""")

        try:
            response = llm.invoke([system_message, human_message])
            raw      = response.content.strip()

            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]

            decisions = json.loads(raw.strip())

            for decision in decisions:
                if decision.get("decision") == "keep":
                    verified_items.append(decision["item"])
                else:
                    rejected_items.append({
                        "item":   decision["item"],
                        "reason": decision.get("reason", "")
                    })

        except Exception as e:
            print(f"   ⚠️ Review batch failed: {e}")
            # If review fails keep all items from this batch
            verified_items.extend(batch)
            continue

    print(f"   ✅ Kept:     {len(verified_items)} items")
    print(f"   ❌ Rejected: {len(rejected_items)} items")

    if rejected_items:
        print(f"\n   Rejected items:")
        for r in rejected_items:
            item = r["item"]
            name = (
                item.get("name")            or  # startup_discovery
                item.get("company")         or  # funding_intelligence
                item.get("entity")          or  # comparison
                item.get("insight", "")[:40] or  # sector_report
                "Unknown"
            )
            reason = r.get("reason", "No reason given")
            print(f"   ✗ {name} — {reason}")

    return {
        "original_query": original_query,
        "query_plan":     query_plan,
        "items":          verified_items,
        "rejected_items": rejected_items,
        "total":          len(verified_items),
        "total_rejected": len(rejected_items)
    }