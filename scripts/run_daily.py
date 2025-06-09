#!/usr/bin/env python3
"""
JobScanner MVP 1 - Daily job crawler script

This script crawls job listings from supported sources and stores them in SQLite.
Designed to be run as a scheduled job (e.g., via GitHub Actions, cron, etc.)
"""

import sys
import os
from datetime import datetime
import logging

# Add the parent directory to the path so we can import jobscanner modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jobscanner.crawler import JobCrawler
from jobscanner.db import JobDatabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jobscanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the daily job crawling process."""
    logger.info("🚀 Starting JobScanner daily crawl")
    
    try:
        # Initialize database
        logger.info("📁 Initializing database...")
        db = JobDatabase("jobs.db")
        
        # Get initial stats
        initial_stats = db.get_stats()
        logger.info(f"📊 Initial stats: {initial_stats}")
        
        # Initialize crawler
        logger.info("🕸️  Initializing crawler...")
        crawler = JobCrawler()
        
        # Define search terms for senior engineering roles
        search_terms = [
            'VP Engineering',
            'Director Engineering',
            'Engineering Manager', 
            'Staff Engineer',
            'Principal Engineer',
            'Senior Engineering Manager',
            'Head of Engineering',
            'Chief Technology Officer',
            'CTO'
        ]
        
        # Define target locations (Israel + Western Europe)
        locations = [
            'Israel',
            'United Kingdom', 
            'Germany',
            'Netherlands',
            'France',
            'Switzerland',
            'Sweden',
            'Denmark',
            'Norway',
            'Austria',
            'Belgium',
            'Ireland',
            'Finland'
        ]
        
        # Crawl all sources
        logger.info(f"🔍 Starting crawl for {len(search_terms)} search terms in {len(locations)} locations...")
        jobs = crawler.crawl_all_sources(search_terms, locations)
        
        if not jobs:
            logger.warning("⚠️  No jobs found during crawl")
            return
        
        # Save jobs to database
        logger.info(f"💾 Saving {len(jobs)} jobs to database...")
        new_jobs_count = 0
        duplicate_count = 0
        
        for job in jobs:
            try:
                job_id = db.insert_job(job)
                if job_id:
                    new_jobs_count += 1
                    logger.debug(f"✅ Saved job: {job['title']} at {job['company']}")
                else:
                    duplicate_count += 1
                    logger.debug(f"⏭️  Skipped duplicate: {job['title']} at {job['company']}")
            except Exception as e:
                logger.error(f"❌ Error saving job {job.get('title', 'Unknown')}: {e}")
        
        # Get final stats
        final_stats = db.get_stats()
        logger.info(f"📊 Final stats: {final_stats}")
        
        # Summary
        logger.info("="*50)
        logger.info("📋 CRAWL SUMMARY")
        logger.info("="*50)
        logger.info(f"🔍 Jobs found: {len(jobs)}")
        logger.info(f"✅ New jobs saved: {new_jobs_count}")
        logger.info(f"⏭️  Duplicates skipped: {duplicate_count}")
        logger.info(f"📈 Total jobs in database: {final_stats['total']}")
        logger.info(f"🆕 New jobs in database: {final_stats['new']}")
        logger.info("="*50)
        
        # Show sample of new jobs
        if new_jobs_count > 0:
            logger.info("🎯 Sample of new jobs found:")
            recent_jobs = db.get_jobs(status='new', limit=5)
            for job in recent_jobs:
                logger.info(f"  • {job['title']} @ {job['company']} ({job['location']})")
        
        logger.info("✅ JobScanner daily crawl completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error during crawl: {e}")
        raise


if __name__ == "__main__":
    main()
