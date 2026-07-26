# Installation Guide

## 1. Local Machine Installation

### OS Requirements
- **Linux/macOS**: Fully supported.
- **Windows**: Supported via PowerShell or WSL2.

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/JobHunterAI.git
cd JobHunterAI
```

### Step 2: Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3: Frontend Setup
```bash
# Install dependencies from the root
npm install --prefix frontend
```

### Step 4: Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Fill in your API keys for Groq or Gemini.

## 2. Docker Installation

If you have Docker installed, you can start the entire stack with one command:

```bash
docker-compose up -d
```

## 3. Troubleshooting Installation
- **Python version**: Ensure `python --version` returns 3.11 or higher.
- **Node version**: Ensure `node --version` returns 22 or higher.
- **Missing Dependencies**: If `pip install` fails on Windows, you may need the "Build Tools for Visual Studio" for certain C-extensions.
