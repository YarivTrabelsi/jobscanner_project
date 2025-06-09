# Placeholder for job crawler logic

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import logging
from playwright.sync_api import sync_playwright
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobCrawler:
    """Web crawler for job listings from various sources."""
    
    def __init__(self):
        """Initialize the crawler with default settings."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.delay = 2  # Delay between requests in seconds
    
    def crawl_google_careers(self, search_terms: List[str] = None, max_pages: int = 3) -> List[Dict]:
        """
        Crawl Google Careers for job listings.
        
        Args:
            search_terms: List of search terms (e.g., ['VP Engineering', 'Director'])
            max_pages: Maximum number of pages to crawl
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not search_terms:
            search_terms = ['VP Engineering', 'Director Engineering', 'Engineering Manager', 'Staff Engineer']
        
        logger.info(f"Crawling Google Careers for terms: {search_terms}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for term in search_terms:
                    logger.info(f"Searching for: {term}")
                    
                    # Navigate to Google Careers with search
                    search_url = f"https://careers.google.com/jobs/results/?q={term.replace(' ', '%20')}"
                    page.goto(search_url)
                    
                    # Wait for jobs to load
                    page.wait_for_selector('[data-test-id="job-search-result"]', timeout=10000)
                    
                    # Scroll to load more jobs
                    for i in range(max_pages):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                    
                    # Extract job listings
                    job_elements = page.query_selector_all('[data-test-id="job-search-result"]')
                    
                    for job_elem in job_elements:
                        try:
                            job_data = self._extract_google_job(page, job_elem)
                            if job_data:
                                jobs.append(job_data)
                        except Exception as e:
                            logger.error(f"Error extracting Google job: {e}")
                            continue
                    
                    time.sleep(self.delay)
                
                browser.close()
        
        except Exception as e:
            logger.error(f"Error crawling Google Careers: {e}")
        
        logger.info(f"Found {len(jobs)} jobs from Google Careers")
        return jobs
    
    def _extract_google_job(self, page, job_elem) -> Optional[Dict]:
        """Extract job data from a Google Careers job element."""
        try:
            # Extract basic info
            title_elem = job_elem.query_selector('[data-test-id="job-title"]')
            title = title_elem.inner_text().strip() if title_elem else ""
            
            location_elem = job_elem.query_selector('[data-test-id="job-location"]')
            location = location_elem.inner_text().strip() if location_elem else ""
            
            # Get job URL by clicking and extracting from current URL
            job_elem.click()
            time.sleep(1)
            url = page.url
            
            # Extract description from the detail page
            desc_elem = page.query_selector('[data-test-id="job-description"]')
            description = desc_elem.inner_text().strip() if desc_elem else ""
            
            # Go back to results
            page.go_back()
            time.sleep(1)
            
            return {
                'title': title,
                'company': 'Google',
                'location': location,
                'url': url,
                'posted_date': self._get_current_date(),
                'description': description,
                'metadata': {
                    'source': 'google_careers',
                    'crawled_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error extracting Google job data: {e}")
            return None
    
    def crawl_linkedin_jobs(self, search_terms: List[str] = None, max_results: int = 50) -> List[Dict]:
        """
        Crawl LinkedIn public job search for job listings.
        
        Args:
            search_terms: List of search terms
            max_results: Maximum number of results to fetch
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not search_terms:
            search_terms = ['VP Engineering', 'Director Engineering', 'Engineering Manager']
        
        logger.info(f"Crawling LinkedIn Jobs for terms: {search_terms}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for term in search_terms:
                    logger.info(f"Searching LinkedIn for: {term}")
                    
                    # Build LinkedIn search URL
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={term.replace(' ', '%20')}&location=United%20States"
                    page.goto(search_url)
                    
                    # Wait for jobs to load
                    try:
                        page.wait_for_selector('.job-search-card', timeout=10000)
                    except:
                        logger.warning(f"No jobs found for term: {term}")
                        continue
                    
                    # Scroll to load more jobs
                    for i in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                    
                    # Extract job listings
                    job_elements = page.query_selector_all('.job-search-card')[:max_results]
                    
                    for job_elem in job_elements:
                        try:
                            job_data = self._extract_linkedin_job(job_elem)
                            if job_data:
                                jobs.append(job_data)
                        except Exception as e:
                            logger.error(f"Error extracting LinkedIn job: {e}")
                            continue
                    
                    time.sleep(self.delay)
                
                browser.close()
        
        except Exception as e:
            logger.error(f"Error crawling LinkedIn Jobs: {e}")
        
        logger.info(f"Found {len(jobs)} jobs from LinkedIn")
        return jobs
    
    def _extract_linkedin_job(self, job_elem) -> Optional[Dict]:
        """Extract job data from a LinkedIn job element."""
        try:
            # Extract title
            title_elem = job_elem.query_selector('.base-search-card__title')
            title = title_elem.inner_text().strip() if title_elem else ""
            
            # Extract company
            company_elem = job_elem.query_selector('.base-search-card__subtitle')
            company = company_elem.inner_text().strip() if company_elem else ""
            
            # Extract location
            location_elem = job_elem.query_selector('.job-search-card__location')
            location = location_elem.inner_text().strip() if location_elem else ""
            
            # Extract URL
            link_elem = job_elem.query_selector('a[data-tracking-control-name="public_jobs_jserp-result_search-card"]')
            url = link_elem.get_attribute('href') if link_elem else ""
            
            # Extract posted date
            posted_elem = job_elem.query_selector('.job-search-card__listdate')
            posted_date = posted_elem.get_attribute('datetime') if posted_elem else self._get_current_date()
            
            # For LinkedIn, we'll get description later or leave it empty for now
            # as extracting full descriptions requires individual page visits
            description = ""
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'posted_date': posted_date or self._get_current_date(),
                'description': description,
                'metadata': {
                    'source': 'linkedin',
                    'crawled_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job data: {e}")
            return None
    
    def crawl_all_sources(self, search_terms: List[str] = None) -> List[Dict]:
        """
        Crawl all supported job sources.
        
        Args:
            search_terms: List of search terms
        
        Returns:
            Combined list of job dictionaries from all sources
        """
        all_jobs = []
        
        # Default search terms for senior engineering roles
        if not search_terms:
            search_terms = [
                'VP Engineering',
                'Director Engineering', 
                'Engineering Manager',
                'Staff Engineer',
                'Principal Engineer',
                'Senior Engineering Manager'
            ]
        
        logger.info(f"Starting crawl for terms: {search_terms}")
        
        # Crawl Google Careers
        try:
            google_jobs = self.crawl_google_careers(search_terms, max_pages=2)
            all_jobs.extend(google_jobs)
        except Exception as e:
            logger.error(f"Failed to crawl Google Careers: {e}")
        
        # Crawl LinkedIn Jobs
        try:
            linkedin_jobs = self.crawl_linkedin_jobs(search_terms, max_results=30)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            logger.error(f"Failed to crawl LinkedIn Jobs: {e}")
        
        # Remove duplicates based on URL
        unique_jobs = []
        seen_urls = set()
        
        for job in all_jobs:
            if job['url'] and job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs
    
    def _get_current_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().date().isoformat()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
