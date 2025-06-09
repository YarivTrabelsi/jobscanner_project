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

### GitHub Pages Deployment (100% GitHub-hosted!)

**1. Fork this repository to your GitHub account**

**2. Enable GitHub Actions and Pages:**
- Go to your forked repo settings
- Click **"Actions"** → **"General"** → Allow all actions
- Click **"Pages"** → **"Source"** → **"GitHub Actions"**

**3. Trigger the workflow:**
- Go to **"Actions"** tab in your repo
- Click **"🕷️ JobScanner Crawl & Serve API"**  
- Click **"Run workflow"** → **"Run workflow"**
- Wait 3-5 minutes for completion

**4. Access your live API:**
```
🌐 Main Dashboard: https://YOUR_USERNAME.github.io/jobscanner_project/
📊 Stats API: https://YOUR_USERNAME.github.io/jobscanner_project/api/stats.json
💼 Jobs API: https://YOUR_USERNAME.github.io/jobscanner_project/api/jobs.json
🏢 Companies API: https://YOUR_USERNAME.github.io/jobscanner_project/api/companies.json
```

**Replace `YOUR_USERNAME` with your GitHub username**

### Local Development

```bash
# Clone and setup
git clone <your-repo-url>
cd jobscanner_project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Run manual crawl
python scripts/run_daily.py

# Query results locally
python scripts/query_jobs.py --stats --detailed
```

---

## 🔌 API Usage Examples

### **Your Live API URLs**
Once deployed, your API will be available at:
```
🌐 Dashboard: https://YOUR_USERNAME.github.io/jobscanner_project/
📊 Stats: https://YOUR_USERNAME.github.io/jobscanner_project/api/stats.json
💼 Jobs: https://YOUR_USERNAME.github.io/jobscanner_project/api/jobs.json
🏢 Companies: https://YOUR_USERNAME.github.io/jobscanner_project/api/companies.json
🔍 Staff Engineers: https://YOUR_USERNAME.github.io/jobscanner_project/api/search_staff_engineer.json
🔍 VP Engineering: https://YOUR_USERNAME.github.io/jobscanner_project/api/search_vp_engineering.json
```

### **Get Database Statistics**
```bash
curl https://YOUR_USERNAME.github.io/jobscanner_project/api/stats.json
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

### **Get Recent Jobs**
```bash
curl https://YOUR_USERNAME.github.io/jobscanner_project/api/jobs.json
```

### **Search for Staff Engineers**
```bash
curl https://YOUR_USERNAME.github.io/jobscanner_project/api/search_staff_engineer.json
```

### **Get Company Analysis**
```bash
curl https://YOUR_USERNAME.github.io/jobscanner_project/api/companies.json
```

### **Download Raw Database**
```bash
curl -O https://YOUR_USERNAME.github.io/jobscanner_project/data/jobs.db
```

### **JavaScript/Frontend Integration**
```javascript
// Get jobs for your frontend
async function getJobs() {
  const response = await fetch('https://YOUR_USERNAME.github.io/jobscanner_project/api/jobs.json');
  const data = await response.json();
  return data.data.jobs;
}

// Get company analysis
async function getCompanies() {
  const response = await fetch('https://YOUR_USERNAME.github.io/jobscanner_project/api/companies.json');
  const data = await response.json();
  return data.data;
}

// Get stats
async function getStats() {
  const response = await fetch('https://YOUR_USERNAME.github.io/jobscanner_project/api/stats.json');
  const data = await response.json();
  return data.data;
}
```

---

## ☁️ GitHub Pages Static API

JobScanner uses GitHub Actions + GitHub Pages to create a **static API** with the following architecture:

### 🔄 **How It Works:**

1. **Scheduled Crawling**: GitHub Actions runs daily at 9 AM UTC
2. **Data Processing**: Crawls jobs, updates SQLite database, generates JSON files  
3. **Static API Generation**: Creates JSON endpoints for stats, jobs, companies, searches
4. **GitHub Pages Deployment**: Serves JSON files as static API endpoints
5. **Live Web Dashboard**: Interactive HTML dashboard with clickable links

### 📁 **Generated API Structure:**

```
docs/
├── index.html                          # 🌐 Main dashboard
├── api/
│   ├── stats.json                      # 📊 Database statistics
│   ├── jobs.json                       # 💼 Recent 50 jobs
│   ├── jobs_all.json                   # 📋 All jobs (full database)
│   ├── companies.json                  # 🏢 Company analysis
│   ├── search_staff_engineer.json     # 🔍 Staff Engineer roles
│   ├── search_vp_engineering.json     # 🔍 VP Engineering roles
│   └── search_*.json                   # 🔍 Other role searches
└── data/
    └── jobs.db                         # 💾 Raw SQLite database
```

### 🎯 **Features:**

✅ **100% GitHub-hosted**: No external services needed  
✅ **Clickable API Links**: Direct browser access to JSON data  
✅ **Live Web Dashboard**: Interactive HTML interface  
✅ **Daily Auto-updates**: Scheduled crawling via GitHub Actions  
✅ **Raw Data Access**: Download SQLite database directly  
✅ **Multiple Search Views**: Pre-built searches for common roles  

### 📊 **What You Get:**

- **🌐 Web Dashboard**: Beautiful interface with live statistics
- **📊 API Endpoints**: Direct JSON access for integration
- **🔍 Pre-built Searches**: Staff Engineer, VP Engineering, etc.
- **📈 Company Analysis**: Jobs grouped by company with counts
- **💾 Raw Database**: Full SQLite download for custom queries
- **📱 Mobile Friendly**: Responsive design works on any device

### ⚙️ **Customization:**

Edit `.github/workflows/crawl-and-serve.yml` to:
- **Change schedule**: Modify the `cron` expression
- **Add search terms**: Update the `search_terms` list in the workflow  
- **Customize dashboard**: Edit the HTML template
- **Add new endpoints**: Extend the JSON generation script

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
