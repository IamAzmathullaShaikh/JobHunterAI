# Analytics Engine

JobHunterAI provides deep insights into your job search performance.

## 1. Metric Categories

### Conversion Tracking
- **Discovery-to-Application**: Percentage of tracked jobs that you actually applied for.
- **Application-to-Interview**: Success rate of your tailored resumes in securing interviews.
- **Interview-to-Offer**: Final stage conversion metrics.

### Velocity Metrics
- **Application Speed**: Average time from job discovery to application submission.
- **Provider Latency**: How fast each AI provider is processing your tailoring requests.

### Content Analytics
- **Skill Gap Heatmap**: Visualizes which skills you are most frequently missing across all jobs you're interested in.
- **ATS Score Trend**: Tracks if your match scores are improving as you refine your master resume.

## 2. Implementation
- Analytics data is computed on-the-fly from the `Application` and `JobListing` records.
- The **Analytics Engine** in `core/analytics/` performs the aggregations.
- Data is visualized in the **Analytics Dashboard** tab using `Recharts` (or similar chart libraries).

## 3. Data Privacy
All analytics are strictly local. No usage data or performance metrics are sent back to the JobHunterAI maintainers.
