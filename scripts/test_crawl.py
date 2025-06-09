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
        
        # Test with limited search terms and locations
        test_terms = ['Staff Engineer', 'VP Engineering']
        test_locations = ['Israel', 'United Kingdom']
        
        logger.info("🔍 Testing improved crawler with location targeting...")
        try:
            # Test the full crawl_all_sources method with location targeting
            all_jobs = crawler.crawl_all_sources(test_terms, test_locations)
            logger.info(f"✅ Location-targeted crawl: Found {len(all_jobs)} jobs")
            
            # Show sample jobs if found
            if all_jobs:
                for i, job in enumerate(all_jobs[:3]):  # Show first 3 jobs
                    if crawler._is_text_valid(job.get('title', '')) and crawler._is_text_valid(job.get('company', '')):
                        logger.info(f"📋 Sample job {i+1}: {job['title']} @ {job['company']} ({job.get('location', 'Unknown')})")
                        
                        # Test database insertion for first job
                        if i == 0:
                            job_id = db.insert_job(job)
                            if job_id:
                                logger.info(f"✅ Database test: Saved job with ID {job_id}")
                            else:
                                logger.info("ℹ️  Database test: Job already exists (duplicate)")
        
        except Exception as e:
            logger.error(f"❌ Location-targeted crawl test failed: {e}")
        
        # Test individual LinkedIn crawler
        logger.info("🔍 Testing LinkedIn crawler directly...")
        try:
            linkedin_jobs = crawler.crawl_linkedin_jobs(test_terms, max_results=3, locations=['Israel'])
            logger.info(f"✅ LinkedIn Israel test: Found {len(linkedin_jobs)} jobs")
            
            if linkedin_jobs:
                for job in linkedin_jobs:
                    if crawler._is_text_valid(job.get('title', '')) and crawler._is_text_valid(job.get('company', '')):
                        logger.info(f"📋 LinkedIn job: {job['title']} @ {job['company']} ({job.get('location', 'Unknown')})")
        
        except Exception as e:
            logger.error(f"❌ LinkedIn direct test failed: {e}")
        
        # Final database stats
        stats = db.get_stats()
        logger.info(f"📊 Final database stats: {stats}")
        
        logger.info("🎉 Test crawl completed!")
        
    except Exception as e:
        logger.error(f"💥 Test failed: {e}")
        raise


if __name__ == "__main__":
    main() 