"""
Basic Text Crawler using BeautifulSoup and requests
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextCrawler:
    """Basic text crawler for extracting content from web pages."""
    
    def __init__(self, delay: float = 1.0, max_pages: int = 10, use_database: bool = False):
        """
        Initialize the crawler.
        
        Args:
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to crawl
            use_database: Whether to save data to database
        """
        self.delay = delay
        self.max_pages = max_pages
        self.use_database = use_database
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Tracking
        self.visited_urls = set()
        self.crawled_data = []
        self.page_count = 0
        
        # Database setup
        if self.use_database:
            try:
                from database import get_db, init_db
                init_db()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                self.use_database = False
    
    def crawl(self, start_urls: List[str], progress_callback=None) -> List[Dict]:
        """
        Crawl websites starting from the given URLs.
        
        Args:
            start_urls: List of URLs to start crawling from
            progress_callback: Optional callback called with the number of pages crawled after each page
            
        Returns:
            List of dictionaries containing crawled data
        """
        url_queue = start_urls.copy()
        
        while url_queue and self.page_count < self.max_pages:
            url = url_queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            logger.info(f"Crawling: {url}")
            
            try:
                # Fetch and parse the page
                page_data = self._fetch_page(url)
                if page_data:
                    self.crawled_data.append(page_data)
                    self.page_count += 1
                    
                    if progress_callback:
                        progress_callback(self.page_count)
                    
                    # Save to database if enabled
                    if self.use_database:
                        self._save_to_database(page_data)
                    
                    # Extract new links if we haven't reached the limit
                    if self.page_count < self.max_pages:
                        new_links = self._extract_links(url, page_data['html'])
                        for link in new_links:
                            if link not in self.visited_urls and link not in url_queue:
                                url_queue.append(link)
                
                self.visited_urls.add(url)
                
                # Delay between requests
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                self.visited_urls.add(url)
        
        logger.info(f"Crawling completed. Processed {self.page_count} pages.")
        return self.crawled_data
    
    def _fetch_page(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse a single page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary containing page data or None if failed
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text(soup)
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'text': text_content,
                'html': response.text,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Clean text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, base_url: str, html: str) -> List[str]:
        """
        Extract links from HTML content.
        
        Args:
            base_url: Base URL for resolving relative links
            html: HTML content
            
        Returns:
            List of absolute URLs
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Basic filtering
            if self._is_valid_url(absolute_url):
                links.append(absolute_url)
        
        return links
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid for crawling.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc and
                not url.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js'))
            )
        except:
            return False
    
    def _save_to_database(self, data: Dict):
        """
        Save crawled data to database.
        
        Args:
            data: Dictionary containing crawled page data
        """
        if not self.use_database:
            return
            
        try:
            from database import get_db, save_crawled_data
            db = next(get_db())
            save_crawled_data(data, db)
            logger.info(f"Saved to database: {data['url']}")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
    
    def save_to_file(self, filename: str, format: str = 'txt'):
        """
        Save crawled data to file.
        
        Args:
            filename: Output filename
            format: Output format ('txt', 'json')
        """
        if format == 'txt':
            with open(filename, 'w', encoding='utf-8') as f:
                for data in self.crawled_data:
                    f.write(f"URL: {data['url']}\n")
                    f.write(f"Title: {data['title']}\n")
                    f.write(f"Description: {data['description']}\n")
                    f.write(f"Text: {data['text'][:500]}...\n")
                    f.write("-" * 80 + "\n\n")
        
        elif format == 'json':
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filename}")
    
    def get_stats(self) -> Dict:
        """
        Get crawling statistics.
        
        Returns:
            Dictionary with crawling statistics
        """
        stats = {
            'pages_crawled': self.page_count,
            'urls_visited': len(self.visited_urls),
            'data_collected': len(self.crawled_data)
        }
        
        # Add database stats if using database
        if self.use_database:
            try:
                from database import get_db, get_stats as get_db_stats
                db = next(get_db())
                db_stats = get_db_stats(db)
                stats.update(db_stats)
            except Exception as e:
                logger.error(f"Failed to get database stats: {e}")
        
        return stats 