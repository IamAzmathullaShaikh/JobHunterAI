import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import asyncio
import streamlit as st
import asyncio
import pandas as pd
from sqlalchemy.future import select

from database.connection import AsyncSessionLocal
from database.models import JobListing

st.set_page_config(page_title="Discovered Jobs - JobHunterAI", layout="wide")

st.markdown("### 🔍 Discovered Job Listings Pipeline")
st.caption("View and filter raw data entries fetched concurrently across tracking streams.")

async def fetch_jobs_dataframe():
    async with AsyncSessionLocal() as session:
        stmt = select(JobListing).order_by(JobListing.date_scraped.desc())
        res = await session.execute(stmt)
        jobs = res.scalars().all()
        
        if not jobs:
            return pd.DataFrame()
            
        data = []
        for j in jobs:
            data.append({
                "Internal ID": j.id,
                "Platform ID": j.job_id_raw,
                "Title": j.title,
                "Company": j.company_name,
                "Location": j.location,
                "Workplace": j.work_place_type,
                "Source": j.source,
                "Link": j.url,
                "Date Found": j.date_scraped.strftime("%Y-%m-%d %H:%M") if j.date_scraped else ""
            })
        return pd.DataFrame(data)

try:
    df = asyncio.run(fetch_jobs_dataframe())
except Exception as e:
    st.error(f"Failed querying data layers: {str(e)}")
    df = pd.DataFrame()

if df.empty:
    st.info("No job listings scraped yet. Head over to the Home landing page to fire up the crawling pipeline.")
else:
    # Add filtering options inside search ribbons
    search_term = st.text_input("Quick filter by Title or Company Name", "")
    if search_term:
        df = df[df['Title'].str.contains(search_term, case=False) | df['Company'].str.contains(search_term, case=False)]
        
    st.dataframe(
        df,
        column_config={
            "Link": st.column_config.LinkColumn("Application Link")
        },
        hide_index=True,
        use_container_width=True
    )
