#!/usr/bin/env python3
"""
JobHunterAI Streamlit Dashboard
Main dashboard for the AI-powered job hunting assistant
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

# Page configuration
st.set_page_config(
    page_title="JobHunterAI Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .job-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .starred {
        border-left: 4px solid #ffd700;
    }
    .applied {
        border-left: 4px solid #28a745;
    }
    .rejected {
        border-left: 4px solid #dc3545;
    }
    .interviewing {
        border-left: 4px solid #ffc107;
    }
    .offer {
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = API_KEY
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None

def get_api_headers():
    """Get API headers with authentication"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.api_key:
        headers["X-API-Key"] = st.session_state.api_key
    return headers

def fetch_jobs(filters: Dict = None) -> List[Dict]:
    """Fetch jobs from the API"""
    try:
        params = filters or {}
        response = requests.get(
            f"{API_BASE_URL}/jobs",
            params=params,
            headers=get_api_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch jobs: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def fetch_job_details(job_id: int) -> Optional[Dict]:
    """Fetch details for a specific job"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/jobs/{job_id}",
            headers=get_api_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch job details: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching job details: {str(e)}")
        return None

def toggle_star(job_id: int, star: bool) -> bool:
    """Toggle star status for a job"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/jobs/{job_id}/star",
            json={"is_starred": star},
            headers=get_api_headers(),
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error toggling star: {str(e)}")
        return False

def trigger_scrape(search_query: str, location: str, limit: int, job_type: str) -> bool:
    """Trigger a new scraping job"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/scrape",
            json={
                "query": search_query,
                "location": location,
                "limit_per_site": limit,
                "job_type": job_type
            },
            headers=get_api_headers(),
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error triggering scrape: {str(e)}")
        return False

def analyze_job(job_id: int, resume_text: str) -> Optional[Dict]:
    """Analyze a job against a resume"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyse",
            json={
                "job_id": job_id,
                "resume_text": resume_text
            },
            headers=get_api_headers(),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Analysis failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error analyzing job: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 JobHunterAI Dashboard</h1>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        # API Configuration
        api_url = st.text_input("API Base URL", value=API_BASE_URL)
        api_key = st.text_input("API Key (optional)", value=st.session_state.api_key, type="password")

        if api_url != API_BASE_URL or api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            # In a real app, we'd update the global API_BASE_URL here
            st.success("Configuration updated!")

        st.divider()

        # Search controls
        st.subheader("🔍 Job Search")
        search_query = st.text_input("Job Title/Keywords", value="software engineer")
        location = st.text_input("Location", value="Remote")
        limit = st.slider("Results per site", 5, 50, 20)
        job_type = st.selectbox("Job Type", ["Full-Time", "Internship", "Contract", "Part-Time"])

        if st.button("🔍 Search Jobs", type="primary"):
            with st.spinner("Searching for jobs..."):
                success = trigger_scrape(search_query, location, limit, job_type)
                if success:
                    st.success("Search initiated! Refreshing results...")
                    st.session_state.jobs_data = []  # Clear cache to force refresh
                    st.session_state.last_refresh = None
                    st.rerun()
                else:
                    st.error("Failed to initiate search")

        st.divider()

        # Manual refresh
        if st.button("🔄 Refresh Data"):
            st.session_state.jobs_data = []
            st.session_state.last_refresh = None
            st.rerun()

        # Show last refresh time
        if st.session_state.last_refresh:
            st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💼 Job Listings", "📝 Resume Analysis", "📈 Analytics"])

    with tab1:
        show_dashboard()

    with tab2:
        show_job_listings()

    with tab3:
        show_resume_analysis()

    with tab4:
        show_analytics()

def show_dashboard():
    """Show the main dashboard with metrics and overview"""
    st.header("📊 Dashboard Overview")

    # Fetch jobs data if not cached or stale
    if not st.session_state.jobs_data or not st.session_state.last_refresh or \
       (datetime.now() - st.session_state.last_refresh).seconds > 300:  # 5 minute cache
        with st.spinner("Loading job data..."):
            st.session_state.jobs_data = fetch_jobs()
            st.session_state.last_refresh = datetime.now()

    jobs = st.session_state.jobs_data

    if not jobs:
        st.info("No job data available. Click 'Search Jobs' in the sidebar to fetch listings.")
        return

    # Calculate metrics
    total_jobs = len(jobs)
    starred_jobs = len([j for j in jobs if j.get('is_starred', False)])
    # Note: In a real implementation, we'd fetch application status from the API
    # For now, we'll simulate some statuses
    applied_jobs = len([j for j in jobs if j.get('application_status') == 'APPLIED'])
    interviewing_jobs = len([j for j in jobs if j.get('application_status') == 'INTERVIEWING'])
    offer_jobs = len([j for j in jobs if j.get('application_status') == 'OFFER'])

    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Jobs", total_jobs)

    with col2:
        st.metric("⭐ Starred", starred_jobs)

    with col3:
        st.metric("📝 Applied", applied_jobs)

    with col4:
        st.metric("💬 Interviewing", interviewing_jobs)

    with col5:
        st.metric("💰 Offers", offer_jobs)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jobs by Source")
        if jobs:
            source_counts = {}
            for job in jobs:
                source = job.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            if source_counts:
                fig = px.pie(
                    values=list(source_counts.values()),
                    names=list(source_counts.keys()),
                    title="Job Distribution by Source"
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Jobs by Location")
        if jobs:
            location_counts = {}
            for job in jobs:
                location = job.get('location', 'Unknown')
                # Simplify location for better visualization
                if ',' in location:
                    location = location.split(',')[0].strip()
                location_counts[location] = location_counts.get(location, 0) + 1

            # Top 10 locations
            sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            if sorted_locations:
                locations, counts = zip(*sorted_locations)
                fig = px.bar(
                    x=list(locations),
                    y=list(counts),
                    title="Top 10 Job Locations"
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader("Recent Activity")
    if jobs:
        # Sort by date scraped (most recent first)
        sorted_jobs = sorted(jobs, key=lambda x: x.get('date_scraped', ''), reverse=True)
        recent_jobs = sorted_jobs[:5]

        for job in recent_jobs:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{job.get('title', 'N/A')}** at {job.get('company_name', 'N/A')}")
                    st.caption(f"{job.get('location', 'N/A')} • {job.get('source', 'N/A')}")
                with col2:
                    star_status = "⭐" if job.get('is_starred', False) else "☆"
                    if st.button(f"{star_status} Star", key=f"star_{job.get('id')}"):
                        new_status = not job.get('is_starred', False)
                        if toggle_star(job.get('id'), new_status):
                            st.rerun()
                with col3:
                    # Show relative time
                    date_scraped = job.get('date_scraped')
                    if date_scraped:
                        try:
                            if isinstance(date_scraped, str):
                                dt = datetime.fromisoformat(date_scraped.replace('Z', '+00:00'))
                            else:
                                dt = date_scraped
                            time_diff = datetime.now() - dt.replace(tzinfo=None)
                            if time_diff.days > 0:
                                time_str = f"{time_diff.days}d ago"
                            elif time_diff.seconds > 3600:
                                time_str = f"{time_diff.seconds // 3600}h ago"
                            else:
                                time_str = f"{time_diff.seconds // 60}m ago"
                            st.caption(time_str)
                        except:
                            st.caption("Recently")
                st.divider()

def show_job_listings():
    """Show the job listings interface"""
    st.header("💼 Job Listings")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        show_starred_only = st.checkbox("⭐ Show Starred Only")

    with col2:
        source_filter = st.selectbox(
            "Filter by Source",
            ["All"] + list(set([job.get('source', 'Unknown') for job in st.session_state.jobs_data])) if st.session_state.jobs_data else ["All"]
        )

    with col3:
        location_filter = st.text_input("Filter by Location")

    with col4:
        min_score = st.slider("Min Match Score", 0, 100, 0)

    # Apply filters
    filtered_jobs = st.session_state.jobs_data.copy()

    if show_starred_only:
        filtered_jobs = [j for j in filtered_jobs if j.get('is_starred', False)]

    if source_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j.get('source') == source_filter]

    if location_filter:
        filtered_jobs = [j for j in filtered_jobs if location_filter.lower() in j.get('location', '').lower()]

    # Note: match score filtering would require joining with AI analysis data
    # For now, we'll skip this filter as it requires additional API calls

    st.write(f"Showing {len(filtered_jobs)} jobs")

    # Job cards
    for job in filtered_jobs:
        # Determine card class based on status (simulated)
        card_class = "job-card"
        # In a real app, we'd get actual status from API
        # For demo, we'll randomly assign some statuses
        import hashlib
        hash_val = int(hashlib.md5(str(job.get('id', 0)).encode()).hexdigest(), 16)
        status_index = hash_val % 5
        statuses = ["", "applied", "interviewing", "offer", "rejected"]
        status = statuses[status_index]
        if status:
            card_class += f" {status}"

        with st.container():
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.subheader(job.get('title', 'N/A'))
                st.write(f"**{job.get('company_name', 'N/A')}**")
                st.write(f"{job.get('location', 'N/A')} • {job.get('source', 'N/A')}")
                if job.get('job_type'):
                    st.caption(f"{job.get('job_type')} • {job.get('work_place_type', 'Onsite')}")

                # Job description preview
                desc = job.get('description_raw', '')[:200] + "..." if len(job.get('description_raw', '')) > 200 else job.get('description_raw', '')
                if desc:
                    with st.expander("View Description"):
                        st.write(desc)

                # Job URL
                if job.get('url'):
                    st.link_button("Apply Now", job.get('url'))

            with col2:
                # Star button
                is_starred = job.get('is_starred', False)
                star_label = "⭐ Starred" if is_starred else "☆ Star"
                if st.button(star_label, key=f"star_btn_{job.get('id')}"):
                    new_status = not is_starred
                    if toggle_star(job.get('id'), new_status):
                        st.rerun()

                # Show match score if available (would come from AI analysis)
                # For demo, we'll show a placeholder
                st.metric("Match Score", "75%")  # Placeholder

            with col3:
                # Application status (simulated)
                status_colors = {
                    "": "secondary",
                    "applied": "success",
                    "interviewing": "warning",
                    "offer": "success",
                    "rejected": "error"
                }
                status_label = status.capitalize() if status else "Not Applied"
                status_color = status_colors.get(status, "secondary")

                st.button(
                    status_label,
                    key=f"status_{job.get('id')}",
                    help="Application status",
                    type="secondary" if status == "" else ("success" if status in ["applied", "offer"] else "warning" if status == "interviewing" else "error")
                )

                # Quick analyze button
                if st.button("🔍 Analyze", key=f"analyze_{job.get('id')}"):
                    st.session_state.job_to_analyze = job.get('id')
                    st.session_state.active_tab = "📝 Resume Analysis"
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

def show_resume_analysis():
    """Show resume analysis interface"""
    st.header("📝 Resume Analysis")

    # Resume input
    st.subheader("Your Resume")
    resume_text = st.text_area(
        "Paste your resume text here",
        height=200,
        placeholder="Paste your resume text here for analysis against job descriptions..."
    )

    # Job selection for analysis
    st.subheader("Select Job to Analyze")

    if st.session_state.jobs_data:
        job_options = {f"{job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}": job.get('id')
                      for job in st.session_state.jobs_data}

        selected_job_label = st.selectbox(
            "Choose a job to analyze against your resume",
            options=list(job_options.keys()),
            index=0 if job_options else None
        )

        if selected_job_label:
            selected_job_id = job_options[selected_job_label]
            selected_job = next((j for j in st.session_state.jobs_data if j.get('id') == selected_job_id), None)

            if selected_job:
                with st.expander("Job Details", expanded=False):
                    st.write(f"**{selected_job.get('title')}** at {selected_job.get('company_name')}")
                    st.write(f"Location: {selected_job.get('location')}")
                    st.write(f"Source: {selected_job.get('source')}")
                    if selected_job.get('url'):
                        st.link_button("View Job Posting", selected_job.get('url'))

                # Analyze button
                if st.button("🔍 Analyze Match", type="primary"):
                    if not resume_text.strip():
                        st.error("Please paste your resume text first.")
                    else:
                        with st.spinner("Analyzing resume against job description..."):
                            result = analyze_job(selected_job_id, resume_text)
                            if result:
                                st.success("Analysis complete!")

                                # Display results
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.metric("Match Score", f"{result.get('match_score', 0):.1f}%")

                                    # Create gauge chart
                                    fig = go.Figure(go.Indicator(
                                        mode = "gauge+number",
                                        value = result.get('match_score', 0),
                                        domain = {'x': [0, 1], 'y': [0, 1]},
                                        title = {'text': "Match Score"},
                                        gauge = {
                                            'axis': {'range': [None, 100]},
                                            'bar': {'color': "darkblue"},
                                            'steps': [
                                                {'range': [0, 50], 'color': "lightgray"},
                                                {'range': [50, 80], 'color': "gray"},
                                                {'range': [80, 100], 'color': "lightgreen"}
                                            ],
                                            'threshold': {
                                                'line': {'color': "red", 'width': 4},
                                                'thickness': 0.75,
                                                'value': 90
                                            }
                                        }
                                    ))
                                    fig.update_layout(height=250)
                                    st.plotly_chart(fig, use_container_width=True)

                                with col2:
                                    st.subheader("Matched Keywords")
                                    matched = result.get('keywords_matched', [])
                                    if matched:
                                        for kw in matched:
                                            st.success(f"✅ {kw}")
                                    else:
                                        st.info("No matched keywords found")

                                    st.subheader("Missing Keywords")
                                    missing = result.get('keywords_missing', [])
                                    if missing:
                                        for kw in missing:
                                            st.warning(f"⚠️ {kw}")
                                    else:
                                        st.success("No missing keywords!")

                                st.subheader("Fit Summary")
                                st.info(result.get('fit_summary', 'No summary available'))
    else:
        st.info("No jobs available for analysis. Please search for jobs first.")

def show_analytics():
    """Show analytics and reporting"""
    st.header("📈 Analytics & Reports")

    if not st.session_state.jobs_data:
        st.info("No data available for analytics. Please search for jobs first.")
        return

    jobs = st.session_state.jobs_data

    # Salary analysis (if available)
    st.subheader("💰 Salary Analysis")
    salary_jobs = [j for j in jobs if j.get('salary_min') is not None or j.get('salary_max') is not None]

    if salary_jobs:
        # Process salary data
        salary_data = []
        for job in salary_jobs:
            min_sal = job.get('salary_min') or 0
            max_sal = job.get('salary_max') or 0
            avg_sal = (min_sal + max_sal) / 2 if min_sal and max_sal else max(min_sal, max_sal)
            currency = job.get('salary_currency', 'USD')

            salary_data.append({
                'title': job.get('title', 'Unknown'),
                'company': job.get('company_name', 'Unknown'),
                'location': job.get('location', 'Unknown'),
                'salary_avg': avg_sal,
                'salary_min': min_sal,
                'salary_max': max_sal,
                'currency': currency,
                'source': job.get('source', 'Unknown')
            })

        if salary_data:
            df_salary = pd.DataFrame(salary_data)

            col1, col2 = st.columns(2)

            with col1:
                fig = px.box(
                    df_salary,
                    x='source',
                    y='salary_avg',
                    title='Salary Distribution by Source',
                    labels={'salary_avg': 'Average Salary', 'source': 'Job Source'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.scatter(
                    df_salary,
                    x='salary_min',
                    y='salary_max',
                    color='source',
                    size='salary_avg',
                    hover_data=['title', 'company', 'location'],
                    title='Salary Range by Source',
                    labels={'salary_min': 'Minimum Salary', 'salary_max': 'Maximum Salary'}
                )
                st.plotly_chart(fig, use_container_width=True)

            # Top paying jobs
            st.subheader("💰 Top Paying Jobs")
            top_jobs = df_salary.nlargest(10, 'salary_avg')[['title', 'company', 'location', 'salary_avg', 'currency', 'source']]
            st.dataframe(top_jobs, use_container_width=True)
        else:
            st.info("No salary data available in the current job listings.")
    else:
        st.info("No salary data available in the current job listings.")

    # Application status analytics (simulated)
    st.subheader("📊 Application Status Distribution")
    # In a real app, this would come from actual application data
    # For demo, we'll simulate some data
    import random
    statuses = ['Not Applied', 'Applied', 'Interviewing', 'Offer', 'Rejected']
    # Generate realistic distribution based on job count
    counts = [
        len(jobs) * 0.6,  # Not Applied
        len(jobs) * 0.25, # Applied
        len(jobs) * 0.1,  # Interviewing
        len(jobs) * 0.03, # Offer
        len(jobs) * 0.02  # Rejected
    ]
    counts = [int(max(0, c)) for c in counts]
    # Adjust to match total
    diff = len(jobs) - sum(counts)
    counts[0] += diff  # Put difference in "Not Applied"

    fig = px.pie(
        values=counts,
        names=statuses,
        title="Application Status Distribution",
        color_discrete_map={
            'Not Applied': 'lightgray',
            'Applied': 'blue',
            'Interviewing': 'orange',
            'Offer': 'green',
            'Rejected': 'red'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    # Activity over time (simulated)
    st.subheader("📈 Job Discovery Trend")
    # Simulate daily job discoveries over past 30 days
    import numpy as np
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    # Simulate some variation in daily discoveries
    base_rate = len(jobs) / 30
    daily_counts = [max(0, int(np.random.normal(base_rate, base_rate * 0.3))) for _ in range(30)]

    df_trend = pd.DataFrame({
        'date': dates,
        'jobs_discovered': daily_counts
    })

    fig = px.line(
        df_trend,
        x='date',
        y='jobs_discovered',
        title='Daily Job Discoveries (Last 30 Days)',
        labels={'jobs_discovered': 'Jobs Discovered', 'date': 'Date'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Export functionality
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export Jobs as CSV"):
            if jobs:
                df = pd.DataFrame(jobs)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"jobhunterai_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    with col2:
        if st.button("📥 Export Analytics Report"):
            # Generate a simple report
            report = f"""
JobHunterAI Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Jobs Analyzed: {len(jobs)}
Starred Jobs: {len([j for j in jobs if j.get('is_starred', False)])}

Sources Breakdown:
"""
            source_counts = {}
            for job in jobs:
                source = job.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                report += f"  {source}: {count}\n"

            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"jobhunterai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()