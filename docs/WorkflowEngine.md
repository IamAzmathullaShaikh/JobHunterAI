# Workflow & CRM Engine

This engine manages the lifecycle of a job application from discovery to offer.

## 1. Kanban Pipeline
The core of the CRM is a Kanban board with the following stages:
1. **Interested**: Newly discovered jobs that look promising.
2. **Tailoring**: Jobs currently being optimized for.
3. **Applied**: Applications that have been submitted.
4. **Interviewing**: Active interview stages.
5. **Negotiating**: Offer received.
6. **Closed**: Offer accepted or candidate rejected.

## 2. Automated Tracking
- **Link Verification**: Periodically checks if the job link is still active.
- **Deadline Alerts**: Notifies the user if a "Saved" job is approaching its application deadline.
- **Activity Logs**: Tracks every action taken (Resume sent, Follow-up email sent, Interview date set).

## 3. Recruiter Outreach
- Integrates with the **Recruiter Finder** to discover hiring managers for a specific role.
- Generates tailored outreach messages for LinkedIn or Email based on the "Match Score" analysis.
