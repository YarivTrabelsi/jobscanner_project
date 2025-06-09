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

## 🎯 MVP 1: Job Crawler + API Backend

This version provides a **REST API** for accessing crawled job data:

✅ **API Endpoints:**
- `GET /api/stats` - Database statistics
- `GET /api/jobs` - List jobs with filtering & pagination
- `GET /api/companies` - Company analysis with job counts  
- `GET /api/search?q=term` - Full-text job search
- `POST /api/crawl` - Trigger manual crawling
- `GET /health` - Service health check

✅ **Data Sources:**
- **Google Careers**: Senior engineering roles
- **LinkedIn Public Jobs**: Leadership positions

✅ **Features:**
- **REST API** with JSON responses
- **Async crawling** with status tracking
- **SQLite database** with deduplication
- **CORS enabled** for frontend integration
- **Real-time search** across job descriptions

---

## 🚀 Quick Start

### Option A: Railway Deployment (Recommended - Free Web API!)

**1. Deploy to Railway:**
- Fork this repository
- Go to [Railway.app](https://railway.app)
- Click "Deploy from GitHub repo"
- Select your forked `jobscanner_project`
- Railway auto-deploys! ✨

**2. Test your API:**
```bash
# Replace YOUR_APP_URL with your Railway app URL
python test_api.py https://YOUR_APP_URL.railway.app
```

**3. Use the API:**
```bash
# Get statistics
curl https://YOUR_APP_URL.railway.app/api/stats

# List jobs
curl https://YOUR_APP_URL.railway.app/api/jobs?limit=10

# Search jobs
curl https://YOUR_APP_URL.railway.app/api/search?q="Staff%20Engineer"

# Trigger manual crawl
curl -X POST https://YOUR_APP_URL.railway.app/api/crawl
```

### Option B: Local Development

```bash
# Clone and setup
git clone <your-repo-url>
cd jobscanner_project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Start API server (runs initial crawl automatically)
python start.py

# Test the API
python test_api.py

# API available at: http://localhost:5000
```

---

## 🔌 API Usage Examples

### **Get Database Statistics**
```bash
curl https://your-app.railway.app/api/stats
```
```json
{
  "success": true,
  "data": {
    "total": 156,
    "new": 12,
    "processed": 144
  },
  "timestamp": "2024-12-07T10:30:00"
}
```

### **List Recent Jobs**
```bash
curl "https://your-app.railway.app/api/jobs?limit=5&status=new"
```

### **Search for Specific Roles**
```bash
curl "https://your-app.railway.app/api/search?q=Staff Engineer&limit=10"
```

### **Get Company Analysis**
```bash
curl https://your-app.railway.app/api/companies
```

### **Trigger Manual Crawl**
```bash
curl -X POST https://your-app.railway.app/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"search_terms": ["VP Engineering", "Director Engineering"]}'
```

### **Check Crawl Status**
```bash
curl https://your-app.railway.app/api/crawl/status
```

### **JavaScript/Frontend Integration**
```javascript
// Get jobs for your frontend
async function getJobs() {
  const response = await fetch('https://your-app.railway.app/api/jobs?limit=20');
  const data = await response.json();
  return data.data.jobs;
}

// Search jobs
async function searchJobs(query) {
  const response = await fetch(`https://your-app.railway.app/api/search?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  return data.data.jobs;
}
```

---

## ☁️ Deployment Options

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
