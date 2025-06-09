#!/usr/bin/env python3
"""
JobScanner Setup Script

Installs required dependencies and sets up the environment.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up JobScanner...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("💡 Tip: You might want to use a virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright Chromium browser"):
        print("❌ Failed to install Playwright browsers")
        print("💡 Try running manually: playwright install chromium")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    print("✅ Created logs directory")
    
    # Test database initialization
    print("🔧 Testing database initialization...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from jobscanner.db import JobDatabase
        
        db = JobDatabase("test_jobs.db")
        stats = db.get_stats()
        print(f"✅ Database initialized successfully (stats: {stats})")
        
        # Clean up test database
        if os.path.exists("test_jobs.db"):
            os.remove("test_jobs.db")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 JobScanner setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run a test crawl: python scripts/run_daily.py")
    print("2. Query results: python scripts/query_jobs.py --stats")
    print("3. View detailed jobs: python scripts/query_jobs.py --detailed")
    print("\n💡 Tips:")
    print("- The crawler uses headless Chrome via Playwright")
    print("- Jobs are stored in jobs.db SQLite database")
    print("- Logs are written to jobscanner.log")


if __name__ == "__main__":
    main() 