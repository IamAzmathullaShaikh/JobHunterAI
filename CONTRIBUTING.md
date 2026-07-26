# Contributing to JobHunterAI

First off, thank you for considering contributing to JobHunterAI! It's people like you that make JobHunterAI such a great tool for the community.

## 🏗 Development Workflow

### 1. Setup
Follow the [Quick Start](README.md#2-installation) guide to set up your local development environment.

### 2. Branching
- All work should be done in a feature branch: `feature/your-feature-name`.
- Bug fixes should use: `fix/bug-description`.
- Release branches: `release/vX.X.X`.

### 3. Coding Standards
- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). Use `black` for formatting and `isort` for imports.
- **Frontend**: Use functional React components and TypeScript. Follow the established Tailwind CSS patterns.
- **Documentation**: All new features must include updated documentation in the `docs/` folder.

### 4. Testing
- Run backend tests: `python -m pytest`
- Run frontend tests: `npm run test`
- Ensure all tests pass before submitting a Pull Request.

## 💬 Pull Request Process
1. Create a detailed description of the changes.
2. Link any related issues.
3. Ensure CI checks pass.
4. Requests will be reviewed by a maintainer within 2-3 business days.

## 🎨 Conventional Commits
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `perf:` for performance improvements
- `chore:` for maintenance tasks

---
Thank you for helping us build the future of AI-powered job searching!
