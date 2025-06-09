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
    
    def crawl_linkedin_jobs(self, search_terms: List[str] = None, max_results: int = 50, locations: List[str] = None) -> List[Dict]:
        """
        Crawl LinkedIn public job search for job listings.
        
        Args:
            search_terms: List of search terms
            max_results: Maximum number of results to fetch
            locations: List of locations to search in
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not search_terms:
            search_terms = ['VP Engineering', 'Director Engineering', 'Engineering Manager']
        
        if not locations:
            # Default to Israel and Western European countries
            locations = [
                'Israel',
                'United Kingdom', 
                'Germany',
                'Netherlands',
                'France',
                'Switzerland',
                'Sweden',
                'Denmark',
                'Norway'
            ]
        
        logger.info(f"Crawling LinkedIn Jobs for terms: {search_terms}")
        logger.info(f"Target locations: {locations}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set more realistic headers to avoid detection
                page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                })
                
                for term in search_terms:
                    for location in locations:
                        logger.info(f"Searching LinkedIn for: {term} in {location}")
                        
                        # Build LinkedIn search URL with location
                        search_url = f"https://www.linkedin.com/jobs/search/?keywords={term.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
                        page.goto(search_url)
                    
                        # Wait for jobs to load
                        try:
                            page.wait_for_selector('.job-search-card', timeout=10000)
                        except:
                            logger.warning(f"No jobs found for term: {term} in {location}")
                            continue
                        
                        # Add random delay to avoid detection
                        time.sleep(2 + (hash(f"{term}{location}") % 3))
                        
                        # Scroll to load more jobs
                        for i in range(2):  # Reduced scrolling to be less aggressive
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(2)
                        
                        # Extract job listings (limit per location to avoid overwhelming)
                        job_elements = page.query_selector_all('.job-search-card')[:min(max_results//len(locations), 10)]
                        
                        for job_elem in job_elements:
                            try:
                                job_data = self._extract_linkedin_job(job_elem, location)
                                if job_data and self._is_text_valid(job_data.get('title', '')):
                                    jobs.append(job_data)
                            except Exception as e:
                                logger.error(f"Error extracting LinkedIn job: {e}")
                                continue
                        
                        time.sleep(self.delay + 1)  # Longer delay between location searches
                
                browser.close()
        
        except Exception as e:
            logger.error(f"Error crawling LinkedIn Jobs: {e}")
        
        logger.info(f"Found {len(jobs)} jobs from LinkedIn")
        return jobs
    
    def _extract_linkedin_job(self, job_elem, search_location: str = "") -> Optional[Dict]:
        """Extract job data from a LinkedIn job element."""
        try:
            # Try multiple selectors for better data extraction
            title_selectors = [
                '.base-search-card__title',
                '.base-search-card__title a',
                '[data-job-title]',
                '.job-search-card__title'
            ]
            
            company_selectors = [
                '.base-search-card__subtitle',
                '.base-search-card__subtitle a',
                '[data-company-name]',
                '.job-search-card__subtitle'
            ]
            
            location_selectors = [
                '.job-search-card__location',
                '.base-search-card__location',
                '[data-job-location]'
            ]
            
            # Extract title with fallback selectors
            title = ""
            for selector in title_selectors:
                title_elem = job_elem.query_selector(selector)
                if title_elem:
                    title = title_elem.inner_text().strip()
                    if title and self._is_text_valid(title):
                        break
            
            # Extract company with fallback selectors
            company = ""
            for selector in company_selectors:
                company_elem = job_elem.query_selector(selector)
                if company_elem:
                    company = company_elem.inner_text().strip()
                    if company and self._is_text_valid(company):
                        break
            
            # Extract location with fallback selectors
            location = search_location  # Use search location as fallback
            for selector in location_selectors:
                location_elem = job_elem.query_selector(selector)
                if location_elem:
                    extracted_location = location_elem.inner_text().strip()
                    if extracted_location and self._is_text_valid(extracted_location):
                        location = extracted_location
                        break
            
            # Extract URL with better selector
            link_elem = job_elem.query_selector('a[href*="/jobs/view/"]') or job_elem.query_selector('a')
            url = link_elem.get_attribute('href') if link_elem else ""
            
            # Clean up URL
            if url and not url.startswith('http'):
                url = f"https://www.linkedin.com{url}"
            
            # Extract posted date
            posted_elem = job_elem.query_selector('.job-search-card__listdate')
            posted_date = posted_elem.get_attribute('datetime') if posted_elem else self._get_current_date()
            
            # Skip if critical fields are missing or invalid
            if not title or not company or not self._is_text_valid(title) or not self._is_text_valid(company):
                return None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'posted_date': posted_date or self._get_current_date(),
                'description': "",  # Leave empty for LinkedIn jobs
                'metadata': {
                    'source': 'linkedin',
                    'search_location': search_location,
                    'crawled_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job data: {e}")
            return None
    
    def crawl_all_sources(self, search_terms: List[str] = None, locations: List[str] = None) -> List[Dict]:
        """
        Crawl all supported job sources.
        
        Args:
            search_terms: List of search terms
            locations: List of locations to search in
        
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
                'Senior Engineering Manager',
                'Head of Engineering'
            ]
        
        # Default to Israel and Western Europe
        if not locations:
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
                'Belgium'
            ]
        
        logger.info(f"Starting crawl for terms: {search_terms}")
        logger.info(f"Target locations: {locations}")
        
        # Crawl Google Careers (still US-focused but may have remote roles)
        try:
            google_jobs = self.crawl_google_careers(search_terms, max_pages=1)
            # Filter Google jobs for international companies
            international_google_jobs = []
            for job in google_jobs:
                if any(loc.lower() in job.get('location', '').lower() or 
                       loc.lower() in job.get('description', '').lower() 
                       for loc in ['remote', 'international', 'europe', 'israel']):
                    international_google_jobs.append(job)
            all_jobs.extend(international_google_jobs)
            logger.info(f"Found {len(international_google_jobs)} relevant Google jobs")
        except Exception as e:
            logger.error(f"Failed to crawl Google Careers: {e}")
        
        # Crawl LinkedIn Jobs with location targeting
        try:
            linkedin_jobs = self.crawl_linkedin_jobs(search_terms, max_results=50, locations=locations)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            logger.error(f"Failed to crawl LinkedIn Jobs: {e}")
        
        # Remove duplicates based on URL and title+company combination
        unique_jobs = []
        seen_urls = set()
        seen_combinations = set()
        
        for job in all_jobs:
            job_key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            url = job.get('url', '')
            
            if (url and url not in seen_urls) or (job_key and job_key not in seen_combinations):
                if url:
                    seen_urls.add(url)
                if job_key:
                    seen_combinations.add(job_key)
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
    
    def _is_text_valid(self, text: str) -> bool:
        """Check if text appears to be valid (not gibberish or obfuscated)."""
        if not text or len(text) < 2:
            return False
        
        # Check for too many special characters (common in obfuscated text)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            return False
        
        # Check for too many asterisks (often used for obfuscation)
        if text.count('*') > len(text) * 0.2:
            return False
        
        # Check for reasonable character distribution
        alpha_ratio = sum(1 for c in text if c.isalpha()) / len(text)
        if alpha_ratio < 0.3:  # At least 30% alphabetic characters
            return False
        
        # Check for extremely long words (common in obfuscated text)
        words = text.split()
        if any(len(word) > 30 for word in words):
            return False
        
        # Check for repeating patterns (common in gibberish)
        if len(set(text.lower().replace(' ', ''))) < len(text) * 0.3:
            return False
        
        return True
