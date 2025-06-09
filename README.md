# JobScanner

**Automated job scanning, analysis, and alerting system for senior engineering roles.**

JobScanner helps senior engineering leaders automatically find, evaluate, and apply for relevant job roles based on real semantic understanding — not just job titles.

---

## 🏗️ System Overview

JobScanner works in stages:

1. **Crawl** job listings daily from company sites and job boards
2. **Analyze** each job's description using LLMs for team size, technical requirements, and seniority level  
3. **Generate** personalized cover letters and resumes based on analysis
4. **Notify** the user via email/WhatsApp
5. **Apply** with user approval

All stages are modular Python components designed for scheduling via GitHub Actions, Railway, or similar free-tier services. Data is stored in SQLite for portability.

---

## 🎯 MVP 1: Job Crawler + Storage

This initial version focuses on crawling and storing job listings:

✅ **Sources Supported:**
- **Google Careers**: https://careers.google.com/jobs/results/
- **LinkedIn Public Jobs**: Dynamic search for engineering leadership roles

✅ **Data Extracted:**
- Job title, company, location, URL
- Posted date and full description  
- Metadata (source, crawl timestamp)

✅ **Storage:**
- SQLite database with deduplication
- Configurable job status tracking
- Full-text search capabilities

---

## 🚀 Quick Start

### Option A: GitHub Actions Deployment (Recommended - Completely Free!)

**1. Fork this repository to your GitHub account**

**2. Enable GitHub Actions in your forked repository:**
- Go to your forked repo on GitHub
- Click "Actions" tab
- Click "I understand my workflows, enable them"

**3. Test the deployment:**
- Go to "Actions" tab in your repo
- Click on "🧪 Test JobScanner Crawler" workflow
- Click "Run workflow" button (top right)
- Click the green "Run workflow" button
- Watch it run! It will take 3-5 minutes

**4. Enable daily crawling:**
- The "🔍 JobScanner Daily Crawl" workflow runs automatically every day at 9 AM UTC
- You can also trigger it manually anytime from the Actions tab

**5. View results:**
- Check the "Actions" tab for crawl summaries
- Download the database from workflow artifacts
- Each run creates a detailed report showing jobs found

### Option B: Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd jobscanner_project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run setup script
python scripts/setup.py

# Start crawling jobs
python scripts/run_daily.py

# View results
python scripts/query_jobs.py --stats --detailed
```

---

## ☁️ GitHub Actions Deployment

JobScanner runs completely free on GitHub Actions with the following architecture:

### 🔄 **How It Works:**

1. **Scheduled Execution**: Runs daily at 9 AM UTC (configurable)
2. **Database Persistence**: SQLite database stored in GitHub Artifacts (90-day retention)
3. **Incremental Updates**: Downloads previous database → adds new jobs → re-uploads
4. **Duplicate Prevention**: URL-based deduplication prevents duplicate job entries
5. **Rich Reporting**: Each run generates a summary with statistics and sample jobs

### 📁 **Workflow Files:**

- `.github/workflows/job-crawler.yml` - Main daily crawler
- `.github/workflows/test-crawler.yml` - Manual testing workflow

### 🎯 **Features:**

✅ **Zero Cost**: Runs on GitHub's free tier  
✅ **Zero Maintenance**: Fully automated scheduling  
✅ **Data Persistence**: Database preserved across runs  
✅ **Rich Logs**: Detailed execution logs and summaries  
✅ **Manual Control**: Trigger runs anytime from GitHub UI  
✅ **Flexible Scheduling**: Easy cron schedule modifications  

### 📊 **Monitoring:**

- **Action Logs**: Real-time execution logs in GitHub Actions tab
- **Job Summaries**: Each run creates a report with statistics
- **Artifact Downloads**: Download the SQLite database anytime
- **Email Notifications**: Get notified if workflows fail (GitHub setting)

### ⚙️ **Customization:**

Edit `.github/workflows/job-crawler.yml` to:
- Change schedule: Modify the `cron` expression
- Adjust search terms: Edit `scripts/run_daily.py`
- Change retention: Modify `retention-days` in workflow
- Add notifications: Integrate with Slack/Discord/email

---

## 📋 Usage Examples

### Basic Crawling
```bash
# Run daily crawl (typically scheduled)
python scripts/run_daily.py
```

### Database Queries
```bash
# Get overview
python scripts/query_jobs.py --stats

# Browse latest jobs with details
python scripts/query_jobs.py --detailed --limit 10

# Find specific companies
python scripts/query_jobs.py --company "Microsoft" --detailed

# Show only unprocessed jobs
python scripts/query_jobs.py --status new --limit 20
```

### Programmatic Access
```python
from jobscanner.db import JobDatabase
from jobscanner.crawler import JobCrawler

# Initialize database
db = JobDatabase("jobs.db")

# Get stats
stats = db.get_stats()
print(f"Total jobs: {stats['total']}")

# Run targeted crawl
crawler = JobCrawler()
jobs = crawler.crawl_google_careers(['Staff Engineer'])

# Save to database
for job in jobs:
    db.insert_job(job)
```

---

## 🗂️ Project Structure

```
jobscanner_project/
├── jobscanner/              # Core modules
│   ├── __init__.py
│   ├── db.py               # SQLite database operations
│   ├── crawler.py          # Web scraping logic
│   ├── analyzer.py         # LLM analysis (future)
│   ├── notifier.py         # Email/WhatsApp alerts (future)
│   └── template_engine.py  # Resume/cover letter generation (future)
├── scripts/                 # Executable scripts
│   ├── setup.py            # Environment setup
│   ├── run_daily.py        # Main crawler script
│   └── query_jobs.py       # Database query tool
├── jobs.db                 # SQLite database (created on first run)
├── jobscanner.log          # Application logs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🛠️ Configuration

### Search Terms

Default search terms target senior engineering roles:
- VP Engineering
- Director Engineering  
- Engineering Manager
- Staff Engineer
- Principal Engineer
- Senior Engineering Manager
- Head of Engineering

Customize by editing `scripts/run_daily.py` or using the crawler programmatically.

### Database Schema

```sql
CREATE TABLE jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  company TEXT, 
  location TEXT,
  url TEXT UNIQUE,                    -- Prevents duplicates
  posted_date TEXT,
  description TEXT,
  status TEXT DEFAULT 'new',          -- 'new', 'processed', etc.
  metadata_json TEXT DEFAULT '{}'     -- JSON for extensibility
);
```

### Rate Limiting

The crawler includes built-in delays and respectful scraping practices:
- 2-second delays between requests
- Headless browser automation
- User-agent rotation
- Error handling and retries

---

## 🔧 Technical Details

### Dependencies
- **requests** + **beautifulsoup4**: HTTP requests and HTML parsing
- **playwright**: Dynamic content and JavaScript-heavy sites  
- **sqlite-utils**: Database operations
- **openai**: LLM integration (future features)
- **twilio**: Notifications (future features)

### Crawling Strategy
- **Google Careers**: Playwright-based scraping with search term injection
- **LinkedIn**: Public job search API with pagination
- **Deduplication**: URL-based duplicate detection
- **Error Handling**: Graceful failures with detailed logging

### Data Flow
1. **Search**: Submit search terms to job sites
2. **Extract**: Parse HTML/JSON responses for job data
3. **Clean**: Normalize text and validate required fields
4. **Store**: Insert into SQLite with duplicate checking
5. **Log**: Comprehensive logging for debugging and monitoring

---

## 🚀 Next Steps (Future MVPs)

### MVP 2: LLM Analysis
- Analyze job descriptions for team size, technical requirements
- Score jobs based on seniority and role fit
- Extract salary ranges and benefits

### MVP 3: Personalization  
- Generate custom cover letters using job analysis
- Tailor resumes for specific roles
- A/B test different application approaches

### MVP 4: Automation
- Auto-apply to pre-approved job types
- Email/WhatsApp notifications for high-value matches
- Integration with job application platforms

---

## 🤝 Contributing

JobScanner is designed for modularity and extensibility:

1. **New Sources**: Add crawler methods in `jobscanner/crawler.py`
2. **Analysis Features**: Extend `jobscanner/analyzer.py` 
3. **Notification Channels**: Implement in `jobscanner/notifier.py`
4. **Data Processing**: Add utilities in core modules

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🆘 Troubleshooting

### Playwright Issues
```bash
# Reinstall browsers
playwright install chromium

# Check browser installation
playwright install --help
```

### Database Issues
```bash
# Reset database
rm jobs.db
python scripts/run_daily.py
```

### Rate Limiting
If you encounter rate limiting:
- Increase delays in `jobscanner/crawler.py`
- Reduce `max_pages` and `max_results` parameters
- Run crawls less frequently

### No Jobs Found
- Check your internet connection
- Verify search terms are valid
- Review logs in `jobscanner.log`
- Some sites may have changed their HTML structure

---

**Happy job hunting! 🎯**
