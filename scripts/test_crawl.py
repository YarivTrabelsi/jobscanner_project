#!/usr/bin/env python3
"""
JobScanner Test Crawler

Quick test to verify the crawler functionality with limited scope.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import jobscanner modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jobscanner.crawler import JobCrawler
from jobscanner.db import JobDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test crawler with limited scope."""
    logger.info("🧪 Running JobScanner test crawl...")
    
    try:
        # Initialize database
        db = JobDatabase("jobs.db")
        
        # Initialize crawler
        crawler = JobCrawler()
        
        # Test with just one search term and limited results
        test_terms = ['Staff Engineer']
        
        logger.info("🔍 Testing Google Careers crawler...")
        try:
            # Just test with 1 page and limited results
            google_jobs = crawler.crawl_google_careers(test_terms, max_pages=1)
            logger.info(f"✅ Google Careers test: Found {len(google_jobs)} jobs")
            
            # Show sample job if found
            if google_jobs:
                sample_job = google_jobs[0]
                logger.info(f"📋 Sample job: {sample_job['title']} @ {sample_job['company']}")
                
                # Test database insertion
                job_id = db.insert_job(sample_job)
                if job_id:
                    logger.info(f"✅ Database test: Saved job with ID {job_id}")
                else:
                    logger.info("ℹ️  Database test: Job already exists (duplicate)")
        
        except Exception as e:
            logger.error(f"❌ Google Careers test failed: {e}")
        
        # Test LinkedIn with very limited scope
        logger.info("🔍 Testing LinkedIn crawler...")
        try:
            linkedin_jobs = crawler.crawl_linkedin_jobs(test_terms, max_results=5)
            logger.info(f"✅ LinkedIn test: Found {len(linkedin_jobs)} jobs")
            
            if linkedin_jobs:
                sample_job = linkedin_jobs[0]
                logger.info(f"📋 Sample LinkedIn job: {sample_job['title']} @ {sample_job['company']}")
        
        except Exception as e:
            logger.error(f"❌ LinkedIn test failed: {e}")
        
        # Final database stats
        stats = db.get_stats()
        logger.info(f"📊 Final database stats: {stats}")
        
        logger.info("🎉 Test crawl completed!")
        
    except Exception as e:
        logger.error(f"💥 Test failed: {e}")
        raise


if __name__ == "__main__":
    main() 