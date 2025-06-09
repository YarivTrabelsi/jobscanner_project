#!/usr/bin/env python3
"""
JobScanner Startup Script

This script:
1. Runs an initial crawl to populate the database (if empty)
2. Starts the Flask API server
"""

import os
import sys
import logging
from jobscanner.db import JobDatabase
from jobscanner.crawler import JobCrawler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_populate_database():
    """Check if database has data, run initial crawl if empty"""
    try:
        db = JobDatabase("jobs.db")
        stats = db.get_stats()
        
        logger.info(f"Database stats: {stats}")
        
        if stats['total'] == 0:
            logger.info("Database is empty, running initial crawl...")
            
            # Run a limited initial crawl
            crawler = JobCrawler()
            jobs = crawler.crawl_all_sources([
                'Staff Engineer', 
                'VP Engineering', 
                'Director Engineering'
            ])
            
            # Save jobs to database
            new_jobs = 0
            for job in jobs:
                job_id = db.insert_job(job)
                if job_id:
                    new_jobs += 1
            
            logger.info(f"Initial crawl completed: {new_jobs} new jobs added")
            
        else:
            logger.info(f"Database already has {stats['total']} jobs, skipping initial crawl")
            
    except Exception as e:
        logger.error(f"Error during initial setup: {e}")
        # Continue anyway - the API can still work without data

def main():
    """Main startup function"""
    logger.info("🚀 Starting JobScanner API Backend...")
    
    # Check and populate database if needed
    check_and_populate_database()
    
    # Import and start the Flask app
    from app import app
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask API on port {port}")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 