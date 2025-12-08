"""
Firecrawl Service
Handles Firecrawl API interactions for crawling any e-commerce website
"""

import time
import logging
import requests
from typing import List, Dict, Optional

try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_SDK_AVAILABLE = True
except ImportError:
    FIRECRAWL_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class FirecrawlService:
    """Service for interacting with Firecrawl API to crawl any e-commerce website"""

    def __init__(self, api_key):
        self.api_key = api_key
        
        # Always initialize base_url and headers for fallback
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if FIRECRAWL_SDK_AVAILABLE:
            # Use official SDK
            try:
                self.app = FirecrawlApp(api_key=api_key)
                self.use_sdk = True
                logger.info("✅ Using Firecrawl official SDK")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Firecrawl SDK: {e}, falling back to raw requests")
                self.use_sdk = False
        else:
            # Fallback to raw requests
            self.use_sdk = False
            logger.warning("⚠️ Firecrawl SDK not available, using raw requests")

    def start_crawl(self, website_url: str, max_pages: int = 50) -> Optional[str]:
        """
        Start crawling a website using Firecrawl
        
        Args:
            website_url: The e-commerce website URL to crawl
            max_pages: Maximum number of pages to crawl
            
        Returns:
            crawl_id: The ID of the crawl job
        """
        try:
            logger.info(f"🔥 Starting Firecrawl for: {website_url}")
            
            if self.use_sdk:
                # Use official SDK - try different method names for different SDK versions
                params = {
                    'limit': max_pages,
                    'scrape_options': {
                        'formats': ['markdown', 'html']
                    }
                }

                logger.info(f"🔍 Using SDK with params: {params}")

                # Try different method names based on SDK version
                try:
                    # v4+ uses async_crawl_url or start_crawl
                    if hasattr(self.app, 'start_crawl'):
                        # Modern SDK (v4+)
                        result = self.app.start_crawl(
                            website_url,
                            limit=max_pages,
                            scrape_options={'formats': ['markdown', 'html']}
                        )
                    elif hasattr(self.app, 'async_crawl_url'):
                        result = self.app.async_crawl_url(website_url, **params)
                    elif hasattr(self.app, 'crawl_url'):
                        result = self.app.crawl_url(website_url, wait_until_done=False, **params)
                    elif hasattr(self.app, 'crawl'):
                        # Older SDK version - pass params as keyword arguments
                        result = self.app.crawl(website_url, **params)
                    else:
                        logger.error(f"❌ No suitable crawl method found in SDK")
                        logger.error(f"❌ Available methods: {dir(self.app)}")
                        return None
                    
                    # Extract crawl_id - handle both object attributes and dict responses
                    crawl_id = None
                    if hasattr(result, 'id'):
                        # SDK returns an object (CrawlResponse/CrawlJob)
                        crawl_id = result.id
                    elif hasattr(result, 'jobId'):
                        crawl_id = result.jobId
                    elif hasattr(result, 'job_id'):
                        crawl_id = result.job_id
                    elif isinstance(result, dict):
                        # Fallback for dict-like responses
                        crawl_id = result.get('id') or result.get('jobId') or result.get('job_id')
                    
                    if crawl_id:
                        logger.info(f"✅ Firecrawl started successfully: {crawl_id}")
                        return crawl_id
                    else:
                        logger.error(f"❌ No crawl ID returned from Firecrawl SDK")
                        logger.error(f"❌ Response type: {type(result)}")
                        logger.error(f"❌ Response attributes: {dir(result)}")
                        return None
                except Exception as sdk_error:
                    logger.error(f"❌ SDK error: {sdk_error}")
                    logger.info(f"🔄 Falling back to raw requests")
                    # Fall through to raw requests
                    self.use_sdk = False
            
            # Fallback to raw requests (or if SDK failed)
            url = f"{self.base_url}/crawl"

            payload = {
                "url": website_url,
                "limit": max_pages,
                "scrapeOptions": {
                    "formats": ["markdown", "html"]
                }
            }
            
            logger.info(f"🔍 Using raw requests with payload: {payload}")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            logger.info(f"🔍 Response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"❌ Response body: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            crawl_id = data.get('id') or data.get('jobId') or data.get('job_id')
            
            if crawl_id:
                logger.info(f"✅ Firecrawl started successfully: {crawl_id}")
                return crawl_id
            else:
                logger.error(f"❌ No crawl ID returned from Firecrawl")
                logger.error(f"❌ Response data: {data}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error starting Firecrawl: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"❌ Response: {e.response.text if hasattr(e.response, 'text') else 'No response text'}")
            raise

    def check_crawl_status(self, crawl_id: str) -> Optional[Dict]:
        """
        Check the status of a Firecrawl job
        
        Args:
            crawl_id: The crawl job ID
            
        Returns:
            dict with status info (status, total, completed, creditsUsed, etc.)
        """
        try:
            if self.use_sdk and hasattr(self.app, 'check_crawl_status'):
                # Use SDK
                try:
                    result = self.app.check_crawl_status(crawl_id)
                    status = result.get('status')
                    total = result.get('total', 0)
                    completed = result.get('completed', 0)
                    
                    logger.info(f"📊 Firecrawl {crawl_id}: {status} ({completed}/{total} pages)")
                    return result
                except Exception as sdk_error:
                    logger.warning(f"⚠️ SDK check_crawl_status failed: {sdk_error}, using raw requests")
                    # Fall through to raw requests
            
            # Raw requests
            url = f"{self.base_url}/crawl/{crawl_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            status = data.get('status')
            total = data.get('total', 0)
            completed = data.get('completed', 0)
            
            logger.info(f"📊 Firecrawl {crawl_id}: {status} ({completed}/{total} pages)")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error checking Firecrawl status: {str(e)}")
            return None

    def wait_for_completion(self, crawl_id: str, timeout: int = 600, poll_interval: int = 10, check_cancelled_callback=None) -> bool:
        """
        Wait for Firecrawl job to complete
        
        Args:
            crawl_id: The crawl job ID
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            check_cancelled_callback: Optional callback function that returns True if job was cancelled
            
        Returns:
            True if succeeded, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if job was cancelled by user
            if check_cancelled_callback and check_cancelled_callback():
                logger.info(f"🛑 Firecrawl {crawl_id} cancelled by user")
                # Cancel the Firecrawl crawl
                self.cancel_crawl(crawl_id)
                return False
            
            status_data = self.check_crawl_status(crawl_id)
            
            if not status_data:
                logger.error(f"❌ Could not get status for crawl {crawl_id}")
                return False
            
            status = status_data.get('status')
            
            if status == 'completed':
                logger.info(f"✅ Firecrawl {crawl_id} completed successfully")
                return True
            elif status == 'failed':
                logger.error(f"❌ Firecrawl {crawl_id} failed")
                return False
            
            logger.info(f"⏳ Waiting for Firecrawl {crawl_id}... ({status})")
            time.sleep(poll_interval)
        
        logger.error(f"⏱️ Firecrawl {crawl_id} timed out after {timeout}s")
        return False

    def get_crawled_pages(self, crawl_id: str) -> List[Dict]:
        """
        Get all crawled pages from a completed Firecrawl job
        
        Args:
            crawl_id: The crawl job ID
            
        Returns:
            List of page dictionaries with markdown, html, and metadata
        """
        try:
            if self.use_sdk:
                # Try SDK methods for getting crawl results
                try:
                    # Try different SDK method names
                    if hasattr(self.app, 'get_crawl_status'):
                        result = self.app.get_crawl_status(crawl_id)
                    elif hasattr(self.app, 'check_crawl_status'):
                        result = self.app.check_crawl_status(crawl_id)
                    else:
                        # No SDK method available, fall back to raw requests
                        logger.warning(f"⚠️ No SDK method for getting crawl results, using raw requests")
                        raise AttributeError("No suitable SDK method found")
                    
                    # Extract pages from result
                    pages = []
                    if hasattr(result, 'data'):
                        pages = result.data
                    elif isinstance(result, dict):
                        pages = result.get('data', [])
                    
                    # Convert Pydantic Document objects to dicts if needed
                    pages = self._normalize_pages(pages)
                    
                    logger.info(f"📄 Retrieved {len(pages)} pages from Firecrawl {crawl_id}")
                    return pages
                except Exception as sdk_error:
                    logger.warning(f"⚠️ SDK get pages failed: {sdk_error}, using raw requests")
                    # Fall through to raw requests
            
            # Raw requests
            url = f"{self.base_url}/crawl/{crawl_id}"
            response = requests.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('data', [])
            
            logger.info(f"📄 Retrieved {len(pages)} pages from Firecrawl {crawl_id}")
            return pages
            
        except Exception as e:
            logger.error(f"❌ Error getting crawled pages: {str(e)}")
            return []
    
    def _normalize_pages(self, pages: List) -> List[Dict]:
        """
        Convert SDK Document objects to dictionaries
        
        Args:
            pages: List of pages (may be Document objects or dicts)
            
        Returns:
            List of page dictionaries
        """
        normalized = []
        for page in pages:
            if isinstance(page, dict):
                # Already a dict
                normalized.append(page)
            elif hasattr(page, 'model_dump'):
                # Pydantic v2 model
                normalized.append(page.model_dump())
            elif hasattr(page, 'dict'):
                # Pydantic v1 model
                normalized.append(page.dict())
            else:
                # Try to convert to dict manually
                page_dict = {}
                for attr in ['url', 'markdown', 'html', 'metadata']:
                    if hasattr(page, attr):
                        page_dict[attr] = getattr(page, attr)
                normalized.append(page_dict)
        
        return normalized

    def cancel_crawl(self, crawl_id: str) -> bool:
        """
        Cancel an ongoing Firecrawl job
        
        Args:
            crawl_id: The crawl job ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            logger.info(f"🛑 Cancelling Firecrawl job: {crawl_id}")
            
            if self.use_sdk and hasattr(self.app, 'cancel_crawl'):
                # Use SDK if available
                try:
                    result = self.app.cancel_crawl(crawl_id)
                    logger.info(f"✅ Firecrawl job {crawl_id} cancelled via SDK")
                    return True
                except Exception as sdk_error:
                    logger.warning(f"⚠️ SDK cancel failed: {sdk_error}, using raw requests")
                    # Fall through to raw requests
            
            # Raw requests - DELETE endpoint
            url = f"{self.base_url}/crawl/{crawl_id}"
            response = requests.delete(url, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Firecrawl job {crawl_id} cancelled successfully")
                return True
            else:
                logger.error(f"❌ Failed to cancel crawl {crawl_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cancelling Firecrawl job {crawl_id}: {str(e)}")
            return False

    def crawl_and_wait(self, website_url: str, max_pages: int = 50, timeout: int = 600) -> List[Dict]:
        """
        Convenience method: Start crawl and wait for completion
        
        Args:
            website_url: The e-commerce website URL to crawl
            max_pages: Maximum number of pages to crawl
            timeout: Maximum time to wait for completion
            
        Returns:
            List of crawled pages
        """
        crawl_id = self.start_crawl(website_url, max_pages)
        
        if not crawl_id:
            logger.error("❌ Failed to start crawl")
            return []
        
        success = self.wait_for_completion(crawl_id, timeout)
        
        if not success:
            logger.error("❌ Crawl did not complete successfully")
            return []
        
        return self.get_crawled_pages(crawl_id)
