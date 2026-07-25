# Developer Guide

Welcome to the JobHunterAI development environment! This guide will help you get started with contributing to the project.

## 1. Development Environment Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 22 or higher
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
npm install
```

## 2. Running in Development Mode

### Start the Backend
```bash
# From the project root
python backend/main.py
```
The API will be available at `http://localhost:8000`. You can view the interactive documentation (Swagger) at `http://localhost:8000/docs`.

### Start the Frontend
```bash
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

## 3. Coding Standards

### Python (Backend)
- Follow **PEP 8**.
- Use **Type Hints** for all function signatures.
- All new logic should be implemented in `core/` or `domain/`.
- Use `Pydantic` for data validation.

### TypeScript (Frontend)
- Use **functional components** and hooks.
- Use **Tailwind CSS** for all styling.
- Maintain strict type safety; avoid `any`.

## 4. Testing

### Backend Tests
We use **Pytest**.
```bash
pytest tests/
```

### Frontend Tests
We use **Vitest**.
```bash
npm run test
```

## 5. Adding a New AI Provider
1. Define the provider interface in `domain/providers/ai.py`.
2. Implement the client in `core/providers/ai/`.
3. Register the provider in the `SmartRouter` located in `core/intelligence/router.py`.
