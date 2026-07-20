import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import asyncio
from loguru import logger

from database.connection import AsyncSessionLocal
from services.job_service import JobService
from services.export_service import ExportService
from services.contact_finder import ContactFinderService
from ai.resume_parser import ResumeParser
from utils.file_parser import extract_text_from_file

# Streamlit Page Setup
st.set_page_config(
    page_title="JobHunterAI — Command Cockpit", 
    page_icon="⚡",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Header Section
st.title("⚡ JobHunterAI Command Cockpit")
st.caption("Autonomous Job Ingestion Fleet • AI Alignment & Resume Profiling • Recruiter Contact X-Ray")
st.markdown("---")

# Session State Initialization
if "parsed_profile" not in st.session_state:
    st.session_state.parsed_profile = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# =========================================================================
# ⚙️ Section 1: Candidate Profiling & Ingestion Telemetry
# =========================================================================
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    with st.container(border=True):
        st.subheader("📄 Candidate Resume Ingestion")
        st.caption("Parse candidate profiles with Groq LLM to automatically infer target roles and key skills.")

        uploaded_file = st.file_uploader("Attach Candidate Resume (PDF / DOCX)", type=["pdf", "docx", "txt"])
        
        if uploaded_file and st.button("🔍 Extract Profile Capabilities via Groq", type="secondary", use_container_width=True):
            with st.spinner("Analyzing candidate text and mapping skill vectors..."):
                try:
                    raw_bytes = uploaded_file.read()
                    raw_text = extract_text_from_file(raw_bytes, uploaded_file.name)
                    st.session_state.resume_text = raw_text
                    
                    parser = ResumeParser()
                    profile_dto = asyncio.run(parser.parse_resume(raw_text))
                    st.session_state.parsed_profile = profile_dto
                    st.success("Candidate Profile Successfully Mapped!")
                except Exception as parse_err:
                    st.error(f"Failed to process resume: {str(parse_err)}")

        # Candidate Profile Card
        if st.session_state.parsed_profile:
            p = st.session_state.parsed_profile
            st.markdown("---")
            st.markdown("##### 👤 Active Candidate Profile")
            st.markdown(f"**Candidate:** {p.full_name or 'Azmathulla Shaik'}")
            st.markdown(f"**Experience:** ~{p.total_experience_years} Years")
            st.markdown(f"**Education:** {', '.join(p.education) if p.education else 'B.Tech CSE'}")
            
            st.markdown("**Identified Core Skills:**")
            st.write(" ".join([f"`{skill}`" for skill in p.key_skills]))
            
            if p.recommended_search_queries:
                st.markdown("**Suggested Search Vectors:**")
                st.code(" | ".join(p.recommended_search_queries))

    with st.container(border=True):
        st.subheader("🎛️ Search Parameters")
        
        default_query = "Territory Sales Executive"
        if st.session_state.parsed_profile and st.session_state.parsed_profile.recommended_search_queries:
            default_query = st.session_state.parsed_profile.recommended_search_queries[0]

        search_input = st.text_input("Target Search Keyword", value=default_query)
        location_input = st.text_input("Geofence / Target Location", value="Andhra Pradesh, India")
        
        job_type_select = st.selectbox(
            "Employment Classification",
            ["Full-Time", "Internship", "Apprenticeship"],
            index=0
        )

with right_col:
    with st.container(border=True):
        st.subheader("🖥️ Fleet Telemetry & Execution")
        st.caption("Dispatches 9 parallel scraping engines: LinkedIn, Indeed, Naukri, Foundit, Glassdoor, Google Jobs, Apify Cloud, Internshala, & YC Jobs.")
        
        console_box = st.empty()
        console_box.info("Pipeline Idle. Ready to initiate ingestion based on profile criteria.")
        
        trigger_pipeline = st.button("🚀 Execute 9-Engine Ingestion & AI Alignment", type="primary", use_container_width=True)
        
        if trigger_pipeline:
            if not search_input or not location_input:
                st.error("Execution halt: Search query and location parameters are required.")
            else:
                console_box.warning(f"Spawning 9-Engine Scraping Fleet for '{search_input}' in '{location_input}'...")
                
                profile_context = st.session_state.resume_text
                if st.session_state.parsed_profile:
                    p = st.session_state.parsed_profile
                    profile_context = (
                        f"Candidate: {p.full_name}\n"
                        f"Target Roles: {', '.join(p.target_roles)}\n"
                        f"Skills: {', '.join(p.key_skills)}\n"
                        f"Education: {', '.join(p.education)}\n"
                        f"Summary: {' '.join(p.experience_highlights)}"
                    )

                async def run_core_pipeline_sequence():
                    async with AsyncSessionLocal() as session:
                        service = JobService(session=session)
                        
                        console_box.info("Phase 1/2: Scraping active listings & applying deduplication guards...")
                        new_jobs = await service.discover_new_listings(
                            search_query=search_input,
                            location=location_input,
                            limit=10,
                            job_type=job_type_select
                        )
                        
                        console_box.info(f"Phase 2/2: Ingestion complete ({len(new_jobs)} unique listings). Evaluating Groq AI match scores...")
                        analyzed_count = await service.process_pending_analyses(user_profile=profile_context)
                        
                        return len(new_jobs), analyzed_count

                try:
                    scraped, analyzed = asyncio.run(run_core_pipeline_sequence())
                    console_box.success(
                        f"Pipeline Execution Complete!\n\n"
                        f"• Unique Harvested Jobs: **{scraped}**\n"
                        f"• AI Skill-Fit Evaluations Completed: **{analyzed}**"
                    )
                    st.balloons()
                except Exception as pipeline_err:
                    logger.error(f"Pipeline failed: {str(pipeline_err)}")
                    console_box.error(f"Execution error: {str(pipeline_err)}")

# =========================================================================
# 🎯 Section 2: Recruiter Outreach & Decision Maker Contact Finder
# =========================================================================
st.markdown("---")
with st.container(border=True):
    st.header("🎯 Recruiter & Decision-Maker Contact Finder")
    st.caption("Locate founders, hiring managers, and recruiters on LinkedIn and X (Twitter) for direct cold outreach.")

    outreach_col1, outreach_col2 = st.columns([1, 1], gap="large")

    with outreach_col1:
        target_company_input = st.text_input("Target Company Name", value="Prayag Marketing")
        target_role_input = st.text_input("Target Role Title", value=search_input)

        find_contacts_btn = st.button("🔍 Find Decision Makers & Draft Cold Message", type="secondary", use_container_width=True)

    with outreach_col2:
        if find_contacts_btn:
            if not target_company_input:
                st.warning("Please enter a company name to generate outreach links.")
            else:
                with st.spinner("Generating X-Ray search vectors and AI cold message..."):
                    finder = ContactFinderService()
                    dto = asyncio.run(finder.find_hiring_contacts(target_company_input, target_role_input))
                    
                    st.markdown("#### 🔗 Direct X-Ray Search Queries:")
                    for label, url in dto.suggested_search_queries.items():
                        st.markdown(f"• **[{label}]({url})** *(Opens pre-filtered Google Search)*")
                    
                    st.markdown("#### 💬 Personalized Cold DM Draft:")
                    st.code(dto.cold_outreach_dm_template, language="markdown")
                    st.info("💡 **Pro Tip:** Send this message directly via LinkedIn Connection request or X/Twitter DM for higher response rates!")

# =========================================================================
# 📊 Section 3: Status Tracker, Database Maintenance, & Export
# =========================================================================
st.markdown("---")
with st.container(border=True):
    st.header("📊 Application Status Tracker & Database Controls")
    st.caption("Review ingested roles, clean up duplicate records, and export styled Excel (.xlsx) or Google Sheets workbooks.")

    tracker_col1, tracker_col2 = st.columns([1, 2], gap="large")

    with tracker_col1:
        st.subheader("⚙️ Controls & Exports")
        
        status_filter = st.selectbox(
            "Filter Listings by Status",
            ["All", "Identified", "AI Ready", "Applied", "Interviewing", "Offer", "Rejected"],
            index=0
        )

        if st.button("📥 Generate Styled Excel (.xlsx)", type="primary", use_container_width=True):
            with st.spinner("Formatting openpyxl workbook and status palettes..."):
                try:
                    async def fetch_excel():
                        async with AsyncSessionLocal() as session:
                            exporter = ExportService(session=session)
                            return await exporter.generate_styled_excel(status_filter=status_filter)

                    excel_bytes = asyncio.run(fetch_excel())
                    
                    st.download_button(
                        label="💾 Download JobTracker_Export.xlsx",
                        data=excel_bytes,
                        file_name=f"JobHunterAI_Tracker_{status_filter}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("Spreadsheet generated!")
                except Exception as exp_err:
                    st.error(f"Export failed: {str(exp_err)}")

        st.markdown("---")
        st.subheader("🧹 Maintenance")
        if st.button("🧼 Purge Duplicate & Applied Jobs from DB", type="secondary", use_container_width=True):
            with st.spinner("Scanning database records and removing duplicates..."):
                try:
                    async def run_purge():
                        async with AsyncSessionLocal() as session:
                            srv = JobService(session=session)
                            return await srv.purge_duplicates_and_applied()

                    dup_purged, _ = asyncio.run(run_purge())
                    st.success(f"Cleaned database! Purged {dup_purged} duplicate listing records.")
                    st.rerun()
                except Exception as purge_err:
                    st.error(f"Purge failed: {str(purge_err)}")

    with tracker_col2:
        st.subheader("📋 Ingested Roles & Compatibility Board")
        
        async def load_dashboard_table():
            async with AsyncSessionLocal() as session:
                exporter = ExportService(session=session)
                return await exporter.fetch_jobs_dataframe(status_filter=status_filter)

        try:
            df_display = asyncio.run(load_dashboard_table())
            if not df_display.empty:
                st.dataframe(
                    df_display[["Status", "Match Score (%)", "Job Title", "Company", "Location", "Source Portal", "Application URL"]],
                    column_config={
                        "Application URL": st.column_config.LinkColumn("Application URL"),
                        "Match Score (%)": st.column_config.ProgressColumn("Fit Score", format="%.1f%%", min_value=0, max_value=100),
                    },
                    hide_index=True,
                    height=450,
                    use_container_width=True
                )
            else:
                st.warning("No listings found matching the selected status filter.")
        except Exception as tbl_err:
            st.error(f"Could not render database view: {str(tbl_err)}")