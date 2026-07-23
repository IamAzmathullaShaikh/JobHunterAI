import os
import sys
import subprocess
import time
from pathlib import Path

def print_styled(msg, style="info"):
    colors = {
        "info": "\033[94m",
        "success": "\033[92m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    color = colors.get(style, colors["reset"])
    print(f"{color}{msg}{colors['reset']}")

def check_env():
    env_path = Path(".env")
    if not env_path.exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print_styled("Created .env from .env.example", "success")
        else:
            env_path.write_text("PORT=8000\nNODE_ENV=development\nDATABASE_URL=sqlite+aiosqlite:///./jobhunter.db\n")

def update_api_keys():
    print_styled("\n--- AI Engine Configuration ---", "bold")
    print_styled("Provide keys to enable Cloud Tiers (Groq/Gemini). Leave empty to use Tier 3 (Local).", "info")

    keys = {
        "GROQ_API_KEY": "Groq Llama 3.3 (Tier 1 - Fast AI)",
        "GEMINI_API_KEY": "Google Gemini 1.5 (Tier 2 - Deep AI)",
        "APIFY_API_TOKEN": "Apify Cloud (Premium Scraping)"
    }

    # Read current env
    env_dict = {}
    if Path(".env").exists():
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env_dict[k] = v

    updated = False
    for key, desc in keys.items():
        current = env_dict.get(key, "")
        if current and "your_" not in current and current.strip() != "":
            print_styled(f"✔ {desc} is configured.", "success")
            change = input(f"   Update this key? (y/N): ").lower()
            if change != 'y':
                continue

        val = input(f"🔑 Enter {desc}: ").strip()
        if val:
            env_dict[key] = val
            updated = True
            print_styled(f"   Saved {key}.", "success")
        else:
            env_dict[key] = "" # Ensure it's empty for fallback
            updated = True
            print_styled(f"   ⚠️ No key provided. System will FALLBACK to Local Engine (Tier 3) for this provider.", "warning")

    if updated:
        # Re-read to keep other variables
        all_lines = []
        if Path(".env").exists():
            with open(".env", "r") as f:
                all_lines = f.readlines()

        with open(".env", "w") as f:
            written_keys = set()
            for line in all_lines:
                key_found = False
                for k in env_dict:
                    if line.startswith(f"{k}="):
                        f.write(f"{k}={env_dict[k]}\n")
                        written_keys.add(k)
                        key_found = True
                        break
                if not key_found:
                    f.write(line)

            # Add missing keys
            for k, v in env_dict.items():
                if k not in written_keys:
                    f.write(f"{k}={v}\n")

def run_local():
    print_styled("\n🚀 Launching JobHunterAI Local Development Ecosystem...", "bold")

    # 1. Install Requirements
    print_styled("📦 Installing Python dependencies...", "info")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print_styled("📦 Installing Frontend dependencies...", "info")
    subprocess.run("npm install --legacy-peer-deps", shell=True, check=True)

    # 2. Run both using concurrently
    print_styled("⚡ Starting Backend (FastAPI) and Frontend (Vite)...", "success")
    try:
        subprocess.run("npm run dev:all", shell=True)
    except KeyboardInterrupt:
        print_styled("\nStopping services...", "warning")

def deploy_server():
    print_styled("\n🏗️ Preparing Final Production Deployment...", "bold")
    print_styled("This will build the Docker container for web server deployment.", "info")

    confirm = input("Proceed with Docker build? (y/N): ").lower()
    if confirm == 'y':
        print_styled("🐳 Building and starting Docker containers...", "info")
        subprocess.run("docker-compose up --build -d", shell=True)
        print_styled("\n✅ Deployment complete! Your system is running in the background.", "success")
        print_styled("Access the dashboard at http://localhost:8000", "info")
    else:
        print_styled("Deployment cancelled.", "warning")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_styled("""
    ================================================
       JobHunterAI Pro - Enterprise Deployment
    ================================================
    """, "bold")

    check_env()
    update_api_keys()

    print_styled("\nChoose Execution Mode:", "bold")
    print("1. Local Development (Real-time coding, hot-reloading)")
    print("2. Final Production Deployment (Docker / Web Server)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ")

    if choice == '1':
        run_local()
    elif choice == '2':
        deploy_server()
    else:
        print_styled("Exiting setup.", "info")

if __name__ == "__main__":
    main()
