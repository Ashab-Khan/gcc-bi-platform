import streamlit as st
import os
import json
from datetime import datetime
from orchestrator import run_pipeline

# ── PAGE CONFIG ──────────────────────────────────────────
st.set_page_config(
    page_title = "GCC AI & Startup Intelligence Platform",
    page_icon  = "🌍",
    layout     = "wide"
)

# ── CUSTOM CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a5276;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1a5276;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #666;
    }
    .stage-complete {
        color: #27ae60;
        font-weight: bold;
    }
    .stage-running {
        color: #e67e22;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────
st.markdown(
    '<div class="main-header">🌍 GCC AI & Startup Intelligence Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">Automated Business Intelligence for UAE • Saudi Arabia • Qatar • Bahrain • Kuwait • Oman</div>',
    unsafe_allow_html=True
)

st.divider()

# ── EXAMPLE QUERIES ──────────────────────────────────────
st.markdown("#### 💡 Example Queries")

example_queries = [
    "Find AI startups in Saudi Arabia",
    "Compare AI investments in UAE and KSA",
    "Generate a report about GenAI adoption in GCC",
    "Find healthcare AI companies in Riyadh",
    "Which startups raised funding this month in GCC",
    "Top VCs investing in MENA AI startups",
]

# Show examples as clickable buttons in 3 columns
cols = st.columns(3)
for i, example in enumerate(example_queries):
    if cols[i % 3].button(example, use_container_width=True):
        st.session_state["selected_query"] = example

st.divider()

# ── INPUT FORM ───────────────────────────────────────────
st.markdown("#### 🔍 Run Intelligence Pipeline")

col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input(
        label            = "Enter your research query",
        value            = st.session_state.get("selected_query", ""),
        placeholder      = "e.g. Find AI startups in Saudi Arabia...",
        label_visibility = "collapsed"
    )

with col2:
    email = st.text_input(
        label            = "Your email address",
        placeholder      = "your@email.com",
        label_visibility = "collapsed"
    )

run_button = st.button(
    "🚀 Run Pipeline & Send Report",
    type                = "primary",
    use_container_width = True
)

# ── PIPELINE EXECUTION ───────────────────────────────────
if run_button:

    # Validate inputs
    if not query.strip():
        st.error("Please enter a research query.")
        st.stop()

    if not email.strip() or "@" not in email:
        st.error("Please enter a valid email address.")
        st.stop()

    st.divider()
    st.markdown("#### ⚙️ Pipeline Running...")

    # Create placeholders for live stage updates
    stage_placeholder = st.empty()
    progress_bar      = st.progress(0)

    # Stage status tracker
    stages = {
        "1. Query Agent":    "⏳ waiting",
        "2. Research Agent": "⏳ waiting",
        "3. Analysis Agent": "⏳ waiting",
        "4. Review Agent":   "⏳ waiting",
        "5. Report Agent":   "⏳ waiting",
        "6. Email Agent":    "⏳ waiting",
    }

    def update_stages(stage_name, status):
        stages[stage_name] = status
        with stage_placeholder.container():
            cols = st.columns(6)
            for i, (name, s) in enumerate(stages.items()):
                with cols[i]:
                    if "✅" in s:
                        st.success(name.split(". ")[1])
                    elif "🔄" in s:
                        st.warning(name.split(". ")[1])
                    else:
                        st.info(name.split(". ")[1])

    # Update stages visually as pipeline runs
    update_stages("1. Query Agent", "🔄 running")
    progress_bar.progress(10)

    # Run the full pipeline
    with st.spinner("Running 6-agent pipeline... this takes 1-2 minutes"):
        results = run_pipeline(query, email)

    progress_bar.progress(100)

    # Mark all stages complete
    for stage in stages:
        stages[stage] = "✅ done"
    update_stages("6. Email Agent", "✅ done")

    st.divider()

    # ── RESULTS DISPLAY ──────────────────────────────────

    if results.get("status") == "success":

        st.success("✅ Pipeline completed successfully!")

        # Stats row
        st.markdown("#### 📊 Pipeline Results")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{results.get('sources_found', 0)}</div>
                <div class="stat-label">Sources Searched</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{results.get('items_before_review', 0)}</div>
                <div class="stat-label">Items Extracted</div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{results.get('items_after_review', 0)}</div>
                <div class="stat-label">After Review</div>
            </div>""", unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{results.get('items_rejected', 0)}</div>
                <div class="stat-label">Rejected</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Query plan details
        query_plan = results.get("query_plan", {})
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📋 Query Analysis**")
            st.write(f"Type: `{query_plan.get('query_type','')}`")
            st.write(f"Sector: `{query_plan.get('sector','')}`")
            st.write(f"Countries: `{', '.join(query_plan.get('countries',[]))}`")
            st.write(f"Time Period: `{query_plan.get('time_period', 'recent')}`") 

        with col2:
            st.markdown("**📄 Report Details**")
            st.write(f"Title: {results.get('report_title','')}")
            st.write(f"File: `{os.path.basename(results.get('report_file',''))}`")
            st.write(f"Email: {'✅ Sent' if results.get('email_sent') else '❌ Failed'}")
            st.write(f"Sources: `{results.get('sources_found', 0)} web pages searched`") 

        # Download button
        st.divider()
        report_file = results.get("report_file", "")
        if report_file and os.path.exists(report_file):
            with open(report_file, "rb") as f:
                st.download_button(
                    label               = "⬇️ Download Report (.docx)",
                    data                = f,
                    file_name           = os.path.basename(report_file),
                    mime                = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width = True
                )

        st.info(f"📧 Report also sent to **{email}** — check your inbox (and spam folder).")

    elif results.get("status") == "no_data":
        st.warning("⚠️ No data found for this query.")
        st.info("Try rephrasing your query or wait a minute if rate limited.")

    else:
        st.error(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")

# ── PAST REPORTS ─────────────────────────────────────────
st.divider()
st.markdown("#### 📁 Past Reports")

outputs_dir = "/tmp/outputs" if os.path.exists("/tmp") else "outputs"
if os.path.exists(outputs_dir):
    files = sorted(
        [f for f in os.listdir(outputs_dir) if f.endswith(".docx")],
        reverse = True
    )
    if files:
        for filename in files[:10]:
            col1, col2 = st.columns([4, 1])
            col1.write(f"📄 {filename}")
            filepath = os.path.join(outputs_dir, filename)
            with open(filepath, "rb") as f:
                col2.download_button(
                    label     = "Download",
                    data      = f,
                    file_name = filename,
                    mime      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key       = filename
                )
    else:
        st.info("No reports generated yet. Run a query above!")
else:
    st.info("No reports generated yet. Run a query above!")

# ── FOOTER ───────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#888; font-size:0.8rem;'>
    GCC AI & Startup Intelligence Platform •
    Powered by LangGraph + Groq + Tavily •
    Built by Khan
</div>
""", unsafe_allow_html=True)