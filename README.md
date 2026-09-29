---
title: GCC AI & Startup Intelligence Platform
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🌍 GCC AI & Startup Intelligence Platform

A Multi-Agent Business Intelligence platform that automatically researches, extracts, and delivers professional reports about GCC startups, funding, and AI markets. Built to deeply understand multi-agent AI architecture — not just ship a demo, but to hit real engineering problems (LLM token limits, data quality filtering, dynamic query understanding, batch processing) and document how each one was diagnosed and solved.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Pipeline-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔍 **Any GCC research query** — startups, funding, comparisons, sector reports, hiring, investors
- 🤖 **6-agent AI pipeline** — each agent specializes in one task and passes clean output to the next
- 🌍 **All 6 GCC countries** — UAE, Saudi Arabia, Qatar, Bahrain, Kuwait, Oman
- 📄 **Professional Word reports** — auto-generated .docx with title page, executive summary, data table, and detailed profiles
- 📧 **Automatic email delivery** — report sent to any email address as attachment
- ✅ **Quality filtering** — Review Agent removes irrelevant, low-quality, or mismatched entries before the report is written

---

## 🎬 Demo

**Live app:** [https://huggingface.co/spaces/Ashabk/gcc-bi-platform](https://huggingface.co/spaces/Ashabk/gcc-bi-platform)

| Query Type | Example Query |
|---|---|
| Startup Discovery | `Find AI startups in Saudi Arabia` |
| Funding Intelligence | `Which startups raised funding in GCC in 2026` |
| Comparison | `Compare AI investments in UAE and KSA` |
| Sector Report | `Generate a report about GenAI adoption in GCC` |
| Hiring Intelligence | `Which companies in UAE are hiring AI engineers` |
| Investor Research | `Top VCs investing in Saudi Arabia AI startups` |

---

## 🏗️ How it works

```
┌─────────────────────┐
│    User Query        │
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Query Agent        │  ← understands intent, detects countries,
│                      │    sector, query type, plans 8-11 searches,
│                      │    selects preferred GCC sources
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Research Agent     │  ← runs targeted web searches via Tavily,
│                      │    prioritizes GCC-specific sources,
│                      │    collects 25-35 unique web pages
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Analysis Agent     │  ← extracts structured data in batches
│                      │    of 6 sources to avoid token limits,
│                      │    dynamic fields per query type
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Review Agent       │  ← quality control: keep/reject per item,
│                      │    removes global companies with small
│                      │    offices, government bodies, duplicates
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Report Agent       │  ← generates professional .docx with
│                      │    title page, executive summary,
│                      │    overview table, detailed profiles
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Email Agent        │  ← sends report as Word attachment
│                      │    via SendGrid with HTML email body
└──────┬───────────────┘
       ▼
┌─────────────────────┐
│   Dashboard          │  ← Streamlit UI with example queries,
│                      │    pipeline stats, download button,
│                      │    past reports history
└─────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) (Docker deployment) |
| Orchestration | Custom Python pipeline (sequential agent coordination) |
| LLM | openai/gpt-oss-120b [Groq](https://groq.com) |
| Web Search | [Tavily](https://tavily.com) |
| Email | [SendGrid](https://sendgrid.com) |
| Report Generation | [python-docx](https://python-docx.readthedocs.io) |
| Deployment | Hugging Face Spaces (Docker) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com)
- A free [Tavily API key](https://tavily.com)
- A free [SendGrid API key](https://sendgrid.com)

### Installation

```bash
git clone https://github.com/AshabK/gcc-bi-platform.git
cd gcc-bi-platform

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_verified_sender_email@gmail.com
```

### Run it

```bash
streamlit run app.py
```

---

## 🔧 Engineering decisions & honest tradeoffs

This is the part of the README that actually matters. Building and deploying this surfaced several real problems — here's what they were and how each was diagnosed and resolved.

<details>
<summary><strong>Why batch processing in the Analysis Agent?</strong></summary>

<br>

The first version of the Analysis Agent sent all 25-35 web sources to the LLM in one request. This immediately hit Groq's token-per-minute limit (6,000 TPM on the free tier) and crashed with a 413 error. The fix was to split sources into batches of 6, process each independently, then merge and deduplicate results. This solved the token limit problem permanently and made the pipeline resilient — if one batch fails, the others still complete and the pipeline continues rather than crashing entirely.

</details>

<details>
<summary><strong>Why a dedicated Review Agent instead of stricter extraction prompts?</strong></summary>

<br>

Early testing showed the Analysis Agent consistently extracted irrelevant entries: Indian IT companies with Saudi offices, government ministries, global giants like Microsoft and GE that appeared in articles about the GCC market. Tightening the extraction prompt helped but never fully solved it — the LLM would still occasionally include borderline cases. Rather than keep patching one prompt, I separated concerns: the Analysis Agent extracts anything plausible, the Review Agent makes keep/reject decisions with full query context. Each agent is better at its narrower job than one agent trying to do both.

</details>

<details>
<summary><strong>Why dynamic fields per query type instead of a fixed schema?</strong></summary>

<br>

The platform handles six fundamentally different query types — a startup discovery query needs name, product, funding, founded; a hiring query needs company, role, salary, requirements; a comparison query needs entity, metric, value, year. A fixed schema would either be too sparse for some types or force irrelevant fields on others. The Query Agent generates the correct field list for each query type, which flows through the entire pipeline — extraction, deduplication, table columns, and report profiles all adapt dynamically to whatever the Query Agent specified.

</details>

<details>
<summary><strong>Why Tavily instead of direct web scraping?</strong></summary>

<br>

Direct scraping would require handling JavaScript rendering, rate limiting, robots.txt, dynamic content, and anti-bot measures for dozens of different GCC news and startup sites. Tavily handles all of this and returns clean, pre-extracted text content. The tradeoff is that premium sources like MAGNiTT and Crunchbase are paywalled even through Tavily — the platform works around this by running 8-11 varied search queries per request, targeting different angles and sources, to maximize coverage despite individual source limitations.

</details>

<details>
<summary><strong>Known limitation: paywalled startup databases</strong></summary>

<br>

The highest-quality GCC startup data lives behind paywalls on MAGNiTT ($500+/month) and Crunchbase (enterprise pricing). Free web search returns 6-16 verified companies per startup discovery query, which is enough to demonstrate the pipeline but less than a paid data source would return. The architecture is designed so swapping in a paid data source would only require updating the Research Agent — the rest of the pipeline would work unchanged.

</details>

<details>
<summary><strong>Known limitation: Groq free tier daily token limit</strong></summary>

<br>

The free Groq tier allows 100,000 tokens per day across all models. A single pipeline run consumes roughly 8,000-15,000 tokens depending on query type and number of sources. This means approximately 6-12 pipeline runs per day before hitting the limit. The platform handles this gracefully — if the limit is hit mid-pipeline, the affected batch is skipped and results from completed batches are used. A production deployment would use a paid Groq tier or implement model fallback to Gemini Flash (free, 1,500 requests/day).

</details>

<details>
<summary><strong>Why /tmp/outputs instead of a persistent outputs folder?</strong></summary>

<br>

HuggingFace Spaces runs in a Docker container where the working directory is read-only after build. Writing to /tmp/ is the standard approach for ephemeral file storage in containerized deployments. The tradeoff is that generated reports are lost when the container restarts — a production version would upload reports to S3 or similar object storage and return a download URL rather than serving from local disk.

</details>

<details>
<summary><strong>Deployment note: app_port mismatch with Streamlit template</strong></summary>

<br>

The Space was initially created from HuggingFace's Streamlit template, which sets app_port: 8501 in README.md. The Dockerfile exposes port 7860 (HuggingFace's standard port). This mismatch caused HuggingFace to serve the template's default streamlit_app.py instead of the actual app — a silent failure with no error message. Fixed by updating app_port to 7860 in README.md to match the Dockerfile EXPOSE directive.

</details>

---

## 📁 Project Structure

```
.
├── agents/
│   ├── query_agent.py       # Query understanding, intent detection, search planning
│   ├── research_agent.py    # Web search via Tavily, source collection
│   ├── analysis_agent.py    # LLM extraction, batch processing, deduplication
│   ├── review_agent.py      # Quality control, keep/reject decisions
│   ├── report_agent.py      # Word document generation
│   └── email_agent.py       # SendGrid email delivery
├── app.py                   # Streamlit dashboard UI
├── orchestrator.py          # Pipeline coordination, timing, error handling
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔮 What I'd build next

- [ ] Supabase Auth for per-user report history and separation
- [ ] Paid MAGNiTT or Crunchbase API integration for richer startup data
- [ ] Redis for real-time agent progress updates in the dashboard
- [ ] Model fallback to Gemini Flash when Groq daily limit is hit
- [ ] Persistent report storage via S3 or Supabase Storage
- [ ] Scheduled reports — run a query automatically every week and email results
- [ ] Arabic language query support leveraging Arabic RAG experience

---

## 📝 License

MIT — feel free to use this as a reference for your own multi-agent AI projects.

---

*Built as a hands-on deep dive into multi-agent AI architecture, GCC market intelligence, and the debugging that happens when you move from a working local pipeline to a live deployment — and the real engineering decisions that emerge when agents fail, token limits hit, and data quality problems surface at runtime.*
