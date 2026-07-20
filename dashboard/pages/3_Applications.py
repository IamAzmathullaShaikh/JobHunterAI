import sys
from pathlib import Path

# 1. Path anchor resolution
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSessionLocal
from database.models import JobListing, JobApplication, ApplicationStatus
from database.repositories.applications import ApplicationRepository
from schemas.ai import JobApplicationCreate, ApplicationStatusDTO

# Page Configuration Setup
st.set_page_config(page_title="Pipeline Funnel - JobHunterAI", layout="wide")

# Modern Minimalistic Dashboard Styling
st.markdown("""
    <style>
    .kanban-header {
        font-size: 14pt;
        font-weight: 600;
        color: #1e293b;
        padding-bottom: 8px;
        border-bottom: 3px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .job-card-title {
        font-size: 11pt;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .job-card-meta {
        font-size: 9pt;
        color: #64748b;
        margin-bottom: 8px;
    }
    .badge-source {
        background-color: #eff6ff;
        color: #1d4ed8;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 8pt;
        font-weight: 600;
    }
    .badge-score {
        background-color: #f0fdf4;
        color: #15803d;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 8pt;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

async def fetch_pipeline_data():
    """Fetches all jobs alongside their current application tracking states and AI metrics."""
    async with AsyncSessionLocal() as session:
        stmt = select(JobListing).options(
            selectinload(JobListing.application),
            selectinload(JobListing.ai_analysis)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

async def initialize_tracking(job_id: int):
    """Moves a job listing into the active tracking funnel."""
    async with AsyncSessionLocal() as session:
        repo = ApplicationRepository(session)
        dto = JobApplicationCreate(job_id=job_id, status=ApplicationStatusDTO.IDENTIFIED)
        await repo.initialize_application(dto)
        await session.commit()

async def update_tracking_state(app_id: int, status_str: str, current_notes: str):
    """Updates the database state for an active application thread."""
    async with AsyncSessionLocal() as session:
        repo = ApplicationRepository(session)
        status_enum = ApplicationStatusDTO(status_str)
        await repo.update_status(app_id=app_id, new_status=status_enum, notes=current_notes)
        await session.commit()

# Load fresh data from repository layers
try:
    listings = asyncio.run(fetch_pipeline_data())
except Exception as e:
    st.error(f"Database extraction failure: {str(e)}")
    listings = []

untracked_jobs = [j for j in listings if not j.application]
tracked_jobs = [j for j in listings if j.application]

# Global Interface Switcher
view_mode = st.radio("Pipeline View Mode", ["📊 Kanban Board", "📥 Intake Queue Receptors"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

if view_mode == "📊 Kanban Board":
    if not tracked_jobs:
        st.info("No active applications currently tracked. Switch to the 'Intake Queue Receptors' to add some jobs.")
    else:
        # Define 4 core columns for a sleek horizontal Kanban layout
        col_todo, col_applied, col_interview, col_closed = st.columns(4, gap="large")
        
        # Column 1: Identified / AI Ready Stage
        with col_todo:
            st.markdown('<div class="kanban-header">📥 Identified & Ready</div>', unsafe_allow_html=True)
            for j in [x for x in tracked_jobs if x.application.status in [ApplicationStatus.IDENTIFIED, ApplicationStatus.AI_READY]]:
                with st.container(border=True):
                    score_badge = f'<span class="badge-score">🎯 {round(j.ai_analysis.match_score)}% Match</span>' if j.ai_analysis else ''
                    st.markdown(f'<div class="job-card-title">{j.title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta">{j.company_name} • {j.location}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta"><span class="badge-source">{j.source}</span> {score_badge}</div>', unsafe_allow_html=True)
                    
                    # Quick Status Selector inside card footer
                    new_status = st.selectbox("Stage", [s.value for s in ApplicationStatusDTO], index=[s.value for s in ApplicationStatusDTO].index(j.application.status.value), key=f"kb-stat-{j.application.id}")
                    opt_notes = st.text_input("Notes", value=j.application.notes or "", key=f"kb-note-{j.application.id}", placeholder="Add comment...")
                    
                    if st.button("Update Card", key=f"kb-save-{j.application.id}", use_container_width=True):
                        asyncio.run(update_tracking_state(j.application.id, new_status, opt_notes))
                        st.rerun()

        # Column 2: Applied Stage
        with col_applied:
            st.markdown('<div class="kanban-header">🚀 Applied</div>', unsafe_allow_html=True)
            for j in [x for x in tracked_jobs if x.application.status == ApplicationStatus.APPLIED]:
                with st.container(border=True):
                    score_badge = f'<span class="badge-score">🎯 {round(j.ai_analysis.match_score)}%</span>' if j.ai_analysis else ''
                    st.markdown(f'<div class="job-card-title">{j.title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta">{j.company_name} • {j.location}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta"><span class="badge-source">{j.source}</span> {score_badge}</div>', unsafe_allow_html=True)
                    
                    new_status = st.selectbox("Stage", [s.value for s in ApplicationStatusDTO], index=[s.value for s in ApplicationStatusDTO].index(j.application.status.value), key=f"kb-stat-{j.application.id}")
                    opt_notes = st.text_input("Notes", value=j.application.notes or "", key=f"kb-note-{j.application.id}")
                    
                    if st.button("Update Card", key=f"kb-save-{j.application.id}", use_container_width=True):
                        asyncio.run(update_tracking_state(j.application.id, new_status, opt_notes))
                        st.rerun()

        # Column 3: Interviewing Stage
        with col_interview:
            st.markdown('<div class="kanban-header">📅 Interviewing</div>', unsafe_allow_html=True)
            for j in [x for x in tracked_jobs if x.application.status == ApplicationStatus.INTERVIEWING]:
                with st.container(border=True):
                    score_badge = f'<span class="badge-score">🎯 {round(j.ai_analysis.match_score)}%</span>' if j.ai_analysis else ''
                    st.markdown(f'<div class="job-card-title" style="color:#d97706;">{j.title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta">{j.company_name} • {j.location}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta"><span class="badge-source">{j.source}</span> {score_badge}</div>', unsafe_allow_html=True)
                    
                    new_status = st.selectbox("Stage", [s.value for s in ApplicationStatusDTO], index=[s.value for s in ApplicationStatusDTO].index(j.application.status.value), key=f"kb-stat-{j.application.id}")
                    opt_notes = st.text_input("Notes", value=j.application.notes or "", key=f"kb-note-{j.application.id}")
                    
                    if st.button("Update Card", key=f"kb-save-{j.application.id}", use_container_width=True):
                        asyncio.run(update_tracking_state(j.application.id, new_status, opt_notes))
                        st.rerun()

        # Column 4: Offers / Outcome Decisions Stage
        with col_closed:
            st.markdown('<div class="kanban-header">🏆 Outcomes</div>', unsafe_allow_html=True)
            for j in [x for x in tracked_jobs if x.application.status in [ApplicationStatus.OFFER, ApplicationStatus.REJECTED, ApplicationStatus.ARCHIVED]]:
                with st.container(border=True):
                    color_marker = "#16a34a" if j.application.status == ApplicationStatus.OFFER else "#dc2626"
                    st.markdown(f'<div class="job-card-title" style="color:{color_marker};">{j.title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta">{j.company_name} • {j.location}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-card-meta">Status: <b>{j.application.status.value}</b></div>', unsafe_allow_html=True)
                    
                    new_status = st.selectbox("Stage", [s.value for s in ApplicationStatusDTO], index=[s.value for s in ApplicationStatusDTO].index(j.application.status.value), key=f"kb-stat-{j.application.id}")
                    opt_notes = st.text_input("Notes", value=j.application.notes or "", key=f"kb-note-{j.application.id}")
                    
                    if st.button("Update Card", key=f"kb-save-{j.application.id}", use_container_width=True):
                        asyncio.run(update_tracking_state(j.application.id, new_status, opt_notes))
                        st.rerun()

else:
    st.subheader("Discovered Job Intake Funnel")
    st.caption("Instantly index newly crawled web listings directly into your workflow columns.")
    
    if not untracked_jobs:
        st.info("Excellent! Every single crawled job has been pulled safely into your Kanban pipelines.")
    else:
        for j in untracked_jobs:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    score_text = f" | Match Fit: **{round(j.ai_analysis.match_score)}%**" if j.ai_analysis else ""
                    st.markdown(f"📦 **{j.title}** at **{j.company_name}** — *{j.location}*")
                    st.markdown(f"Source: `{j.source}`{score_text}")
                with c2:
                    if st.button("Track Job", key=f"intake-{j.id}", type="primary", use_container_width=True):
                        asyncio.run(initialize_tracking(j.id))
                        st.success("Moved to board!")
                        st.rerun()