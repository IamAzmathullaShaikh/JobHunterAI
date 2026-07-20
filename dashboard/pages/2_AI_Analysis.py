import sys
from pathlib import Path

# 1. Force Python to recognize the root project directory from the subpage level
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# 2. Third-Party Imports
import streamlit as st
import asyncio
import json
import pandas as pd
from sqlalchemy.future import select

# 3. Local Project Platform Imports
from database.connection import AsyncSessionLocal
from database.models import JobListing, AIAnalysis

st.set_page_config(page_title="AI Analysis Matrix - JobHunterAI", layout="wide")

st.markdown("### 🧠 AI Analysis Compatibility Matrix")
st.caption("Review deep alignment vectors, target gaps, and match calculations evaluated via Structured OpenAI Models.")

async def fetch_analyzed_jobs():
    async with AsyncSessionLocal() as session:
        # Join listings against completed AI Analysis evaluations
        stmt = select(JobListing, AIAnalysis).join(AIAnalysis, JobListing.id == AIAnalysis.job_id).order_by(AIAnalysis.match_score.desc())
        res = await session.execute(stmt)
        rows = res.all()
        return rows

try:
    analyzed_rows = asyncio.run(fetch_analyzed_jobs())
except Exception as e:
    st.error(f"Error communicating with database repository: {str(e)}")
    analyzed_rows = []

if not analyzed_rows:
    st.info("No AI evaluations found. Run your discovery pipeline or verify your OpenAI API Key parameters.")
else:
    # Build a clean mapping selector list
    job_options = {f"[{round(row.AIAnalysis.match_score)}%] {row.JobListing.title} at {row.JobListing.company_name}": row for row in analyzed_rows}
    selected_job_key = st.selectbox("Select an evaluated job post to inspect:", list(job_options.keys()))
    
    if selected_job_key:
        match = job_options[selected_job_key]
        job = match.JobListing
        analysis = match.AIAnalysis
        
        # Display detailed score breakdowns
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("Match Fit Score", f"{analysis.match_score}%")
        with c2:
            st.markdown(f"**Fit Strategic Summary:**\n{analysis.fit_summary}")
            
        st.markdown("---")
        
        # Unpack local keywords arrays
        try:
            matched_kws = json.loads(analysis.keywords_matched)
        except Exception:
            matched_kws = []
            
        try:
            missing_kws = json.loads(analysis.keywords_missing)
        except Exception:
            missing_kws = []
            
        kw_col1, kw_col2 = st.columns(2)
        with kw_col1:
            st.success("✨ Matched Profile Keywords / Skills")
            if matched_kws:
                st.write(", ".join([f"`{kw}`" for kw in matched_kws]))
            else:
                st.caption("No overlapping keyword signatures explicitly mapped out.")
                
        with kw_col2:
            # FIXED: Swapped out non-existent st.danger for st.error
            st.error("⚠️ Identified Missing Structural Gaps / Keywords")
            if missing_kws:
                st.write(", ".join([f"`{kw}`" for kw in missing_kws]))
            else:
                st.caption("Excellent! Zero matching requirement gaps caught by the parsing engine.")