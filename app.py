#!/usr/bin/env python3
"""
JobScanner API Backend

A Flask web API that serves crawled job data.
Endpoints:
- GET /api/stats - Database statistics
- GET /api/jobs - List jobs with filtering
- GET /api/jobs/{id} - Get specific job
- POST /api/crawl - Trigger manual crawl
- GET /health - Health check
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import json
import logging
from datetime import datetime
import threading
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from jobscanner.db import JobDatabase
from jobscanner.crawler import JobCrawler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize database
db = JobDatabase("jobs.db")

# Global variables for crawl status
crawl_status = {
    'is_running': False,
    'last_run': None,
    'last_results': None,
    'error': None
}


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected',
        'version': '1.0.0'
    })


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/jobs')
def get_jobs():
    """Get jobs with optional filtering"""
    try:
        # Parse query parameters
        status = request.args.get('status')
        company = request.args.get('company')
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        
        # Get jobs from database
        jobs = db.get_jobs(status=status, limit=limit + offset)
        
        # Apply additional filters
        if company:
            jobs = [job for job in jobs if company.lower() in job['company'].lower()]
        
        # Apply pagination
        paginated_jobs = jobs[offset:offset + limit]
        
        # Parse metadata JSON for each job
        for job in paginated_jobs:
            try:
                job['metadata'] = json.loads(job['metadata_json'])
                del job['metadata_json']
            except:
                job['metadata'] = {}
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': paginated_jobs,
                'total': len(jobs),
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < len(jobs)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/jobs/<int:job_id>')
def get_job(job_id):
    """Get a specific job by ID"""
    try:
        jobs = db.get_jobs(limit=None)
        job = next((j for j in jobs if j['id'] == job_id), None)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Parse metadata
        try:
            job['metadata'] = json.loads(job['metadata_json'])
            del job['metadata_json']
        except:
            job['metadata'] = {}
        
        return jsonify({
            'success': True,
            'data': job,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/companies')
def get_companies():
    """Get list of companies with job counts"""
    try:
        jobs = db.get_jobs(limit=None)
        companies = {}
        
        for job in jobs:
            company = job['company']
            if company not in companies:
                companies[company] = {
                    'name': company,
                    'job_count': 0,
                    'latest_posting': None
                }
            
            companies[company]['job_count'] += 1
            
            # Track latest posting date
            if job['posted_date']:
                if not companies[company]['latest_posting'] or job['posted_date'] > companies[company]['latest_posting']:
                    companies[company]['latest_posting'] = job['posted_date']
        
        # Sort by job count
        sorted_companies = sorted(companies.values(), key=lambda x: x['job_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': sorted_companies,
            'total': len(sorted_companies),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/crawl', methods=['POST'])
def trigger_crawl():
    """Trigger a manual crawl (async)"""
    global crawl_status
    
    if crawl_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Crawl already in progress'
        }), 409
    
    try:
        # Parse request data
        data = request.get_json() or {}
        search_terms = data.get('search_terms', [
            'VP Engineering', 'Director Engineering', 'Engineering Manager'
        ])
        
        # Start crawl in background thread
        thread = threading.Thread(target=run_crawl_async, args=(search_terms,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Crawl started',
            'search_terms': search_terms,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error starting crawl: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/crawl/status')
def get_crawl_status():
    """Get current crawl status"""
    return jsonify({
        'success': True,
        'data': crawl_status,
        'timestamp': datetime.now().isoformat()
    })


def run_crawl_async(search_terms):
    """Run crawl in background thread"""
    global crawl_status
    
    crawl_status['is_running'] = True
    crawl_status['error'] = None
    
    try:
        logger.info(f"Starting async crawl with terms: {search_terms}")
        
        # Initialize crawler
        crawler = JobCrawler()
        
        # Run crawl
        jobs = crawler.crawl_all_sources(search_terms)
        
        # Save to database
        new_jobs = 0
        for job in jobs:
            job_id = db.insert_job(job)
            if job_id:
                new_jobs += 1
        
        # Update status
        crawl_status['last_run'] = datetime.now().isoformat()
        crawl_status['last_results'] = {
            'total_found': len(jobs),
            'new_jobs': new_jobs,
            'duplicates': len(jobs) - new_jobs
        }
        
        logger.info(f"Crawl completed: {new_jobs} new jobs from {len(jobs)} total")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        crawl_status['error'] = str(e)
    
    finally:
        crawl_status['is_running'] = False


@app.route('/api/search')
def search_jobs():
    """Search jobs by title, company, or description"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', type=int, default=20)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Get all jobs and filter
        jobs = db.get_jobs(limit=None)
        matching_jobs = []
        
        query_lower = query.lower()
        for job in jobs:
            # Search in title, company, description
            if (query_lower in job['title'].lower() or 
                query_lower in job['company'].lower() or 
                (job['description'] and query_lower in job['description'].lower())):
                
                # Parse metadata
                try:
                    job['metadata'] = json.loads(job['metadata_json'])
                    del job['metadata_json']
                except:
                    job['metadata'] = {}
                
                matching_jobs.append(job)
        
        # Limit results
        limited_jobs = matching_jobs[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': limited_jobs,
                'total': len(matching_jobs),
                'query': query,
                'limit': limit
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Check if we should run an initial crawl
    if len(sys.argv) > 1 and sys.argv[1] == '--initial-crawl':
        logger.info("Running initial crawl...")
        try:
            crawler = JobCrawler()
            jobs = crawler.crawl_all_sources(['Staff Engineer', 'VP Engineering'])
            
            new_jobs = 0
            for job in jobs:
                job_id = db.insert_job(job)
                if job_id:
                    new_jobs += 1
            
            logger.info(f"Initial crawl completed: {new_jobs} new jobs")
        except Exception as e:
            logger.error(f"Initial crawl failed: {e}")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting JobScanner API on port {port}")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /api/stats - Database statistics") 
    logger.info("  GET  /api/jobs - List jobs")
    logger.info("  GET  /api/jobs/{id} - Get specific job")
    logger.info("  GET  /api/companies - List companies")
    logger.info("  GET  /api/search?q=term - Search jobs")
    logger.info("  POST /api/crawl - Trigger manual crawl")
    logger.info("  GET  /api/crawl/status - Get crawl status")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 