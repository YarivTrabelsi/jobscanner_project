#!/usr/bin/env python3
"""
JobScanner Database Query Tool

Simple CLI tool to query and display jobs from the database.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add the parent directory to the path so we can import jobscanner modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jobscanner.db import JobDatabase


def display_job(job, detailed=False):
    """Display a job in a formatted way."""
    print(f"📍 [{job['id']}] {job['title']}")
    print(f"   🏢 {job['company']} | 📍 {job['location']}")
    print(f"   📅 {job['posted_date']} | 🏷️  {job['status']}")
    
    if detailed:
        print(f"   🔗 {job['url']}")
        if job['description']:
            desc = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
            print(f"   📝 {desc}")
        
        # Parse metadata
        try:
            metadata = json.loads(job['metadata_json'])
            if metadata:
                print(f"   ⚙️  Source: {metadata.get('source', 'unknown')}")
                if 'crawled_at' in metadata:
                    crawled_time = datetime.fromisoformat(metadata['crawled_at'].replace('Z', '+00:00'))
                    print(f"   🕒 Crawled: {crawled_time.strftime('%Y-%m-%d %H:%M')}")
        except:
            pass
    
    print()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Query JobScanner database')
    parser.add_argument('--status', help='Filter by status (new, processed)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed information')
    parser.add_argument('--stats', '-s', action='store_true', help='Show database statistics')
    parser.add_argument('--company', help='Filter by company name')
    
    args = parser.parse_args()
    
    # Initialize database
    db = JobDatabase("jobs.db")
    
    # Show stats if requested
    if args.stats:
        stats = db.get_stats()
        print("📊 DATABASE STATISTICS")
        print("=" * 30)
        print(f"Total jobs: {stats['total']}")
        print(f"New jobs: {stats['new']}")
        print(f"Processed jobs: {stats['processed']}")
        print()
    
    # Query jobs
    jobs = db.get_jobs(status=args.status, limit=args.limit)
    
    # Filter by company if specified
    if args.company:
        jobs = [job for job in jobs if args.company.lower() in job['company'].lower()]
    
    if not jobs:
        print("❌ No jobs found matching criteria")
        return
    
    print(f"🔍 Found {len(jobs)} jobs:")
    print("=" * 50)
    
    for job in jobs:
        display_job(job, detailed=args.detailed)


if __name__ == "__main__":
    main() 