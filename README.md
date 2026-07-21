# JobHunterAI 🚀

JobHunterAI is a comprehensive, local-first job tracking and discovery application. It helps you find relevant jobs across multiple engines, match your resume using AI, and manage your applications via a streamlined Kanban board.

Designed for privacy and efficiency, it runs locally on your machine, with optional AI enhancements powered by Google Gemini.

---

## 📂 Repository Structure

```text
JobHunterAI/
├── src/                # Frontend React code (Vite + Tailwind CSS)
│   ├── components/     # UI Components (Kanban, JobCards, etc.)
│   ├── pages/          # Main application views
│   └── server/         # Node.js server-side bridges
├── scrapers/           # Python Playwright scraper fleet
├── scripts/            # Orchestration and CLI bridge scripts
├── database/           # SQLite models and connection logic (Python)
├── config/             # System and environment settings
├── streamlit/          # Optional Streamlit dashboard
├── server.ts           # Main Express backend entry point
├── db.json             # Local JSON storage (Node.js backend)
├── jobhunter.db        # Local SQLite storage (Python backend)
├── Dockerfile          # Multi-stage build for production
├── docker-compose.yml  # Container orchestration
└── .github/workflows/  # CI/CD pipelines
```

---

## 🛠 Requirements & Dependencies

### Runtime Environments
- **Node.js**: v20.x or higher
- **Python**: v3.10.x or higher
- **Docker**: (Optional) For containerized deployment

### Key Libraries
- **Frontend/Backend**: React, Express, Vite, Google Gen AI, Tailwind CSS, Lucide React, Motion.
- **Scraper Fleet**: Playwright, BeautifulSoup4, SQLAlchemy, Pydantic, Loguru.

---

## 🚀 Local Setup & Running

### 1. Clone the Repository
```bash
git clone https://github.com/IamAzmathullaShaikh/JobHunterAI.git
cd JobHunterAI
```

### 2. Node.js Setup (Frontend & Main Backend)
1. Install dependencies:
   ```bash
   npm install
   ```
2. Create a `.env` file and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   APIFY_API_TOKEN=your_apify_token (Optional)
   ```
3. Start the development server (runs both Vite and Express):
   ```bash
   npm run dev
   ```
   Access the app at `http://localhost:3000`.

### 3. Python Setup (Scraper Fleet)
The scrapers are invoked by the Node server but require their own environment:
1. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

### 4. Optional Streamlit Dashboard
If you want to use the alternative Python-based dashboard:
```bash
streamlit run streamlit/app.py
```

---

## 🐳 Deployment Options

### Docker Deployment
The project includes a multi-stage Dockerfile that bundles both Node.js and the Python scraper fleet.

1. **Build and Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
2. **Environment Variables**:
   Ensure your `.env` file contains the necessary API keys before running the build.

### CI/CD (GitHub Actions)
The repository is configured with a CI/CD pipeline in `.github/workflows/ci-cd.yml`:
- **validate-codebase**: Lints the TypeScript code and performs a test build on every push to `main`.
- **build-docker-image**: Automatically verifies that the Docker image builds successfully.

---

## 🔍 Troubleshooting

### Scraper Failures
- **Python Not Found**: Ensure `python3` is in your PATH. If you use a different name, set `PYTHON_BIN` in your `.env`.
- **Playwright Errors**: If scrapers fail to launch, try running `playwright install --with-deps chromium`.
- **Empty Results**: Some sites have strong anti-bot protections. Using an `APIFY_API_TOKEN` improves reliability via cloud scraping.

### Database Issues
- The Node.js app uses `db.json` for persistence. If the file becomes corrupted, you can safely delete it to reset (you will lose tracked jobs).
- The Python modules use `jobhunter.db`.

---

## 🤝 Contribution Guidelines
1. Branch naming: `feature/feature-name` or `fix/bug-fix-name`.
2. Commit message format: `type(scope): description` (e.g., `fix(scraper): capture resolved URL`).
3. Maintain local-first data integrity.

---

## 📜 Credits and License
Maintained by **IamAzmathullaShaikh**.
Released under the **MIT License**.
