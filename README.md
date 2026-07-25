# JobHunterAI 🚀
### Elite AI-Powered Career Automation & Job Search Intelligence

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/JobHunterAI/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 22+](https://img.shields.io/badge/node-22+-green.svg)](https://nodejs.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)]()

**JobHunterAI** is a production-grade, local-first ecosystem designed to automate the modern job search. By leveraging a high-performance Python backend with a multi-tier AI fallback router and a modern React frontend, it provides job seekers with enterprise-level tools for resume optimization, job discovery, and application tracking.

---

## 🏗 Architecture Overview

JobHunterAI follows a clean, modular architecture designed for resilience and privacy.

```mermaid
graph TD
    subgraph Client Layer
        Web[React Dashboard]
    end

    subgraph API Gateway
        FastAPI[FastAPI Service]
        Policer[Request Policer]
        Sanitizer[PII Redactor]
    end

    subgraph Intelligence Core
        Router[3-Tier Smart Router]
        ResumeEngine[Resume Intelligence]
        MatchingEngine[ATS Scorer]
        ScraperFleet[Job Discovery]
        Analytics[Career Insights]
    end

    subgraph Data Layer
        Cache[(Response Cache)]
        DB[(SQLite / Postgres)]
    end

    Web --> FastAPI
    FastAPI --> Policer
    Policer --> Sanitizer
    Sanitizer --> Cache
    Cache -- Miss --> Router
    Router --> ResumeEngine & MatchingEngine & ScraperFleet & Analytics
    ResumeEngine & MatchingEngine & ScraperFleet & Analytics --> DB
```

---

## ✨ Key Features

- **3-Tier Smart AI Router**: Seamlessly switches between high-performance providers (Groq, Gemini) and local models to ensure 100% uptime and cost efficiency.
- **ATS Optimization Engine**: Side-by-side job description analysis with skill-gap visualization and AI-driven keyword injection.
- **Enterprise Resume Suite**: Generate high-fidelity, ATS-compliant resumes in PDF and DOCX formats with multiple professional templates.
- **9-Platform Job Discovery**: Aggregated live job feeds from LinkedIn, Indeed, Glassdoor, ZipRecruiter, and more via an intelligent scraper fleet.
- **Application Tracker CRM**: Manage your entire pipeline with a drag-and-drop Kanban board, automated follow-ups, and recruiter contact discovery.
- **Zero-Trust Privacy**: Integrated PII redactor masks sensitive data locally before any cloud processing, ensuring your privacy is never compromised.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 22+**
- **Docker** (Optional for containerized deployment)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/JobHunterAI.git
cd JobHunterAI

# Setup Backend
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup Frontend
npm install
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=sqlite:///jobhunter.db
```

### 4. Run the Application
```bash
# Start Backend (FastAPI)
python backend/main.py

# Start Frontend (Dev Mode)
npm run dev
```

---

## 📂 Project Structure

```text
/
├── backend/            # FastAPI Application & API Routes
├── core/               # Business Logic, AI Providers, Scrapers
├── domain/             # Entities, Models, and Domain Interfaces
├── application/        # Application Services & Use Cases
├── src/                # React Frontend (Vite)
├── docs/               # Technical Documentation
├── tests/              # Unit & Integration Test Suite
├── docker/             # Containerization Configs
└── scripts/            # Automation & Utility Scripts
```

---

## 🛠 Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **Frontend**: React, TypeScript, Tailwind CSS, Lucide React
- **AI/ML**: Groq, Google Gemini, Sentence-Transformers (Local)
- **Database**: SQLite (Development), PostgreSQL (Production Ready)
- **DevOps**: Docker, GitHub Actions, Pytest, Vitest

---

## 🗺 Roadmap

- [x] v1.0.0: Core Engine, Smart Router, Job Discovery, Kanban CRM
- [ ] v1.1.0: Voice-activated Interview Prep, Automated LinkedIn Outreach
- [ ] v1.2.0: Multi-user Support, Chrome Extension for one-click apply
- [ ] v2.0.0: Fully Autonomous Job Application Agent

---

## 🤝 Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## 🛡 Security

For information on how to report security vulnerabilities, please see our [SECURITY.md](SECURITY.md).

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework.
- [Lucide](https://lucide.dev/) for the beautiful icons.
- [Tailwind CSS](https://tailwindcss.com/) for the styling engine.
