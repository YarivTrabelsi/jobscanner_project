#!/usr/bin/env python3
"""
JobScanner API Testing Script

Test the API endpoints to make sure everything works.
"""

import requests
import json
import sys
import time

def test_api(base_url="http://localhost:5000"):
    """Test all API endpoints"""
    
    print(f"🧪 Testing JobScanner API at: {base_url}")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            tests.append(True)
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        tests.append(False)
    
    # Test 2: Stats endpoint
    print("2. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            print(f"   ✅ Stats: {stats}")
            tests.append(True)
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
        tests.append(False)
    
    # Test 3: Jobs endpoint
    print("3. Testing jobs endpoint...")
    try:
        response = requests.get(f"{base_url}/api/jobs?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', {}).get('jobs', [])
            print(f"   ✅ Found {len(jobs)} jobs")
            if jobs:
                print(f"   📋 Sample job: {jobs[0]['title']} @ {jobs[0]['company']}")
            tests.append(True)
        else:
            print(f"   ❌ Jobs failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Jobs error: {e}")
        tests.append(False)
    
    # Test 4: Companies endpoint
    print("4. Testing companies endpoint...")
    try:
        response = requests.get(f"{base_url}/api/companies", timeout=10)
        if response.status_code == 200:
            data = response.json()
            companies = data.get('data', [])
            print(f"   ✅ Found {len(companies)} companies")
            if companies:
                print(f"   🏢 Top company: {companies[0]['name']} ({companies[0]['job_count']} jobs)")
            tests.append(True)
        else:
            print(f"   ❌ Companies failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Companies error: {e}")
        tests.append(False)
    
    # Test 5: Crawl status endpoint
    print("5. Testing crawl status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/crawl/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('data', {})
            print(f"   ✅ Crawl status: {status}")
            tests.append(True)
        else:
            print(f"   ❌ Crawl status failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Crawl status error: {e}")
        tests.append(False)
    
    # Test 6: Manual crawl trigger (optional)
    if "--test-crawl" in sys.argv:
        print("6. Testing manual crawl trigger...")
        try:
            response = requests.post(
                f"{base_url}/api/crawl", 
                json={"search_terms": ["Test Engineer"]},
                timeout=10
            )
            if response.status_code == 200:
                print("   ✅ Crawl triggered successfully")
                
                # Wait and check status
                print("   ⏳ Waiting 30 seconds to check progress...")
                time.sleep(30)
                
                status_response = requests.get(f"{base_url}/api/crawl/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    crawl_status = status_data.get('data', {})
                    if crawl_status.get('is_running'):
                        print("   🔄 Crawl still running...")
                    else:
                        results = crawl_status.get('last_results', {})
                        print(f"   ✅ Crawl completed: {results}")
                
                tests.append(True)
            else:
                print(f"   ❌ Crawl trigger failed: {response.status_code}")
                tests.append(False)
        except Exception as e:
            print(f"   ❌ Crawl trigger error: {e}")
            tests.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the API deployment.")
        return False

def main():
    """Main function"""
    base_url = "http://localhost:5000"
    
    # Check for custom URL
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        base_url = sys.argv[1]
    
    print(f"JobScanner API Test Suite")
    print(f"Target URL: {base_url}")
    print(f"Use --test-crawl to include crawl testing")
    print()
    
    success = test_api(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 