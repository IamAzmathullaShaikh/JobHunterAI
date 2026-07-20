# JobHunterAI

JobHunterAI is an automated, local-first job tracking and discovery application. It helps you find relevant jobs, match your resume against them, and track your applications in a streamlined Kanban board. The system is designed to run locally, ensuring your data remains yours, with optional AI capabilities to enhance your job search.

## Quick Start

### 1. Prerequisites
- **Node.js**: (v18 or higher)
- **Git**: to clone the repository

### 2. Local Setup
1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/IamAzmathullaShaikh/JobHunterAI.git
   cd JobHunterAI
   \`\`\`
2. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`
3. (Optional) Create a \`.env\` file in the root directory if you plan to use AI features:
   \`\`\`env
   GEMINI_API_KEY=your_gemini_api_key
   \`\`\`
4. Start the application:
   \`\`\`bash
   npm run dev
   \`\`\`
   Access the app at \`http://localhost:3000\`.

### Using Docker
1. Ensure Docker and Docker Compose are installed.
2. Run the application:
   \`\`\`bash
   docker-compose up --build
   \`\`\`

## Project Structure
- \`/src\`: Frontend React code (Vite + Tailwind CSS).
- \`/server.ts\`: Backend Express server handling API routes.
- \`/database\`: Local JSON database (db.json) handling data persistence.
- \`package.json\`: Project dependencies and scripts.

## Installation and Requirements
- **Node.js**: Requires Node.js version 18+.
- **NPM**: Package manager to run scripts.

## Running the System
- **Development**: Run \`npm run dev\` to start both the Vite dev server and Express backend.
- **Production Build**: Run \`npm run build\` and then \`npm start\`.
- **AI Modules**: AI matching and scraping features are optional. If \`GEMINI_API_KEY\` is not present, the app falls back to local deterministic parsers and mock data.

## Troubleshooting

### Broken Job Links
**Issue**: Clicking a job in the UI shows an error or points to the wrong job.
**Fix applied**: The app now stores both \`raw_url\` and \`canonical_url\`. The deduplication key uses a robust fingerprint (\`title + company + location + portal_id\`). The UI binds to \`canonical_url\` and shows a user-friendly expired job message if the link is missing.
**Verification**: Check \`server.ts\` logs for `[Scraper]` and `[Normalizer]` to trace job records.

## Testing
Currently, the pipeline can be tested by inspecting the console logs during the ingestion process:
- Scraper logs output the raw generated listings.
- Normalizer logs the addition of unique jobs to the local DB.

## Docker and CI/CD
- **Docker Compose**: Sets up the app environment easily with a simple \`docker-compose up\`.
- **GitHub Actions**: (If configured) Automates linting and builds on every push to the \`main\` branch.

## Contribution Guidelines
1. Branch naming: \`feature/feature-name\` or \`fix/bug-fix-name\`.
2. Commit message format: \`type(scope): description\` (e.g., \`fix(scraper): capture resolved URL\`).
3. Rule: Maintain local-first data integrity.

## Credits and License
Maintained by IamAzmathullaShaikh.
Released under the MIT License.
