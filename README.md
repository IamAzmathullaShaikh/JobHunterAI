# ⚡ JobHunterAI Command Cockpit

> **Autonomous Career Intelligence, Multi-Board Job Discovery, and AI Application Tracking Infrastructure**

JobHunterAI is a high-performance, full-stack TypeScript application built with **Express (Node.js)** on the backend, **React 18 + Vite + Tailwind CSS** on the frontend, and powered by **Google Gemini (gemini-3.5-flash)**. It automates candidate resume profiling, simulates cross-site job board ingestion, performs deep AI alignment evaluation, drafts personalized recruiter outreach campaigns, and manages your active job applications inside a visual Kanban tracker.

---

## 🌟 Key Features & Capabilties

### 1. 📄 Candidate Resume Ingestion & Profiling
- **Skill Extraction:** Parses raw resume text or PDF documents to map professional capabilities, education histories, and cumulative years of experience.
- **Dynamic Search Vectors:** Automatically constructs target search keywords (e.g., `Territory Sales Executive`, `Software Engineer`) and geofenced queries for job discovery engines.
- **Strictly Server-Side LLM Parsing:** Processes files and text securely on the backend using the official `@google/genai` SDK, ensuring API keys are never exposed to the client browser.

### 2. 🕷️ 9-Engine Ingestion Pipeline (Simulated)
Simultaneously simulates keyword crawling across 9 popular platforms:
- **Professional Networks & Portals:** LinkedIn, Indeed, Glassdoor, Google Jobs.
- **Niche & regional boards:** Naukri (India focus), Foundit, YC Jobs (WorkAtAStartup), Internshala.
- **Web scraping actors:** Apify Cloud integrations.
- **Guarded Deduplication:** Automatically rejects duplicates and excludes roles already present in your pipeline.

### 3. 🧠 AI Alignment & Match Scoring Matrix
- **Gemini Compatibility Score:** Computes a quantitative compatibility score ($0-100\%$) between your resume profile and crawled job requirements.
- **Requirement Gap Auditing:** Extracts matching professional keywords and pinpoints missing skills or qualifications to help you prepare for interviews.
- **Fit Strategic Summary:** Generates contextual analysis explaining alignment strengths and strategic recommendations.
- **Batch Evaluation:** Automatically runs parallel background compatibility audits for pending roles.

### 4. 📊 Kanban Board & Tracking Funnel
- **Dynamic Status Columns:** Organize listings across statuses (`Identified`, `Applied`, `Interviewing`, `Offer`, `Rejected`, `Archived`).
- **Interactive Notes:** Keep track of interview dates, points of contact, and custom application diaries.
- **Intake Queue:** Easily review newly discovered job boards and move them into the active tracking column with a single click.

### 5. 🎯 Recruiter Contact Finder & Outreach Engine
- **LinkedIn/X (Twitter) X-Ray Queries:** Generates precise Google search query links that bypass platform limitations to target hiring managers, founders, or talent acquisition leads.
- **Personalized DM Drafts:** Pre-fills polite, high-converting cold outreach connection messages tailored to the specific role and company.

### 6. 📥 Styled Excel Exports (`.xlsx`)
- **Executive Spreadsheets:** Downloads clean, formatted workbooks. Columns are auto-fitted with color-coded tracking badges for seamless uploads into Google Drive.

---

## 🛠️ Architecture & Tech Stack

### Frontend (Client SPA)
- **Vite + React 18 + TypeScript:** Fast builds, zero runtime overhead.
- **Tailwind CSS:** Custom twilight dark palette with balanced padding, margins, and typography.
- **Framer Motion (`motion/react`):** Micro-interactions and fluid visual transitions.
- **Lucide React:** Icon vectors.

### Backend (Server API)
- **Express + TypeScript:** Production-ready JSON API server.
- **esbuild Bundler:** Bundles backend typescript into a standalone, ultra-fast `dist/server.cjs` file to bypass relative path imports.
- **Google Gen AI SDK (`@google/genai`):** Modern, official Google SDK used for resume parsing and compatibility evaluation.
- **SheetJS (`xlsx`):** Direct server-side generation of Excel spreadsheet files.

---

## 🛠️ Bug Fixes & Code Enhancements Implemented
1. **TypeScript Migration:** Successfully migrated old Python/Streamlit services into a unified, server-side-rendered Node.js React app.
2. **Type Safety & Rigorous Linting:** Adjusted `tsconfig.json` compiler flags to secure compiler checks, resolved unused declarations, and defined full static typing interfaces (`JobListing`, `CandidateProfile`, etc.).
3. **Database Volume Configuration:** Added support for the `DB_PATH` environment variable in `server.ts` to allow easy persistence configuration on Docker environments.
4. **Local Host Security Resolution:** Fixed Vite server `allowedHosts` options inside `vite.config.ts` for safe, seamless local and cloud-based web proxy tunneling.

---

## 📦 Docker Containerization

To run JobHunterAI in an isolated, production-ready environment:

### Prerequisites
- **Docker** and **Docker Compose** installed.

### 1. Configure Environment Variables
Create a `.env` file in the project root:
```env
PORT=3000
NODE_ENV=production
GEMINI_API_KEY=your_actual_google_gemini_api_key
```

### 2. Launching with Docker Compose
Run the following command to build the image and start the container:
```bash
docker-compose up --build -d
```

This starts the application on `http://localhost:3000` and configures a persistent Docker volume (`jobhunter-data`) inside `/app/data` to save your `db.json` database file securely.

### 3. Docker Image Commands
- **Check Container Logs:**
  ```bash
  docker logs -f jobhunter-ai-app
  ```
- **Stop Containers:**
  ```bash
  docker-compose down
  ```

---

## 🚀 Step-by-Step Local Development Guide

### 1. Install Dependencies
Make sure you have Node.js (v20+) installed. Run:
```bash
npm install
```

### 2. Configure Local Settings
Create a `.env` file from the provided template:
```bash
cp .env.example .env
```
Fill in your `GEMINI_API_KEY` with a key from [Google AI Studio](https://aistudio.google.com/).

### 3. Start Development Server
Launch the full-stack server-side application in development mode:
```bash
npm run dev
```
The app will run on `http://localhost:3000`.

### 4. Build and Production Run
To compile both the client React bundles and the backend Express CJS bundle, run:
```bash
npm run build
npm run start
```

---

## 🧪 CI/CD Pipeline (GitHub Actions)

The repository is equipped with a ready-made continuous integration workflow at `.github/workflows/ci-cd.yml` that automatically:
1. Triggers on every push or pull-request to the `main` or `master` branches.
2. Boots up Node.js and installs dependencies safely.
3. Checks for typescript compile issues or linter errors (`npm run lint`).
4. Compiles client static bundles and backend server bundles (`npm run build`).
5. Validates that the multi-stage `Dockerfile` compiles cleanly to prevent broken deployments.

---

## 📜 License
Distributed under the **MIT License**. Free to modify, self-host, and extend!
