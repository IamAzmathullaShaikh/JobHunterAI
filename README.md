# JobHunterAI 🚀
### Elite AI-Powered Career Automation & Job Search Intelligence

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/JobHunterAI/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 22+](https://img.shields.io/badge/node-22+-green.svg)](https://nodejs.org/)

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
        ResumeEngine[Resume V2]
        Coach[AI Interview Coach]
        ScraperFleet[Job Discovery]
        Analytics[Mission Control]
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
    Router --> ResumeEngine & Coach & ScraperFleet & Analytics
    ResumeEngine & Coach & ScraperFleet & Analytics --> DB
```

---

## ✨ Key Features

- **3-Tier Smart AI Router**: Seamlessly switches between Groq, Gemini, and local models based on task capability and health.
- **AI Interview Coach**: practice mock interviews with real-time scoring and STAR method guidance grounded in your resume.
- **Production Resume Builder**: Multi-document management with 10 professional A4 templates and high-fidelity PDF/DOCX exports.
- **Recruiter CRM**: Discover Hiring Managers and Recruiters via live intelligence and manage outreach history.
- **Intelligent Job Discovery**: Aggregated live job feeds from LinkedIn and Glassdoor with automated deduplication and AI enrichment.
- **Unified Mission Control**: Career dashboard with chronological timelines, success rates, and skill-gap radar.
- **Zero-Trust Privacy**: Integrated PII redactor masks sensitive data locally before any cloud processing.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 22+**
- **PostgreSQL** (Optional, defaults to SQLite)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/JobHunterAI.git
cd JobHunterAI

# Setup Backend
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Setup Frontend
cd frontend
npm install
npm run build
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### 4. Run the Application
```bash
# Start Production Server
python backend/main.py
```

---

## 🛠 Technology Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic, Alembic
- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide React
- **AI/ML**: Groq (Llama 3.3), Google Gemini, Ollama
- **Data**: PostgreSQL, Redis (Caching), Pandas
- **Export**: Playwright (PDF), python-docx, Markdown

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework.
- [Lucide](https://lucide.dev/) for the beautiful icons.
- [Tailwind CSS](https://tailwindcss.com/) for the styling engine.
