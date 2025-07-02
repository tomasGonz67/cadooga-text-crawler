"""
Example usage of the basic text crawler with database integration
"""

from crawler import TextCrawler
from database import get_db, get_crawled_pages, get_stats as get_db_stats

crawler_instance = None
crawler_results = None

def run_example_crawler(progress_callback=None):
    """Run the example crawler and return the crawler instance and results. Calls progress_callback(pages_crawled) after each page if provided."""
    global crawler_instance, crawler_results
    crawler_instance = TextCrawler(
        delay=1.0,
        max_pages=10,
        use_database=True
    )
    start_urls = [
        'https://portfolio-beige-ten-56.vercel.app/',
    ]
    crawler_instance.crawled_data = []  # ensure clean
    results = crawler_instance.crawl(start_urls, progress_callback=progress_callback)
    crawler_results = results
    crawler_instance.save_to_file('crawled_data.txt', format='txt')
    crawler_instance.save_to_file('crawled_data.json', format='json')
    return crawler_instance, results

def main():
    """Example of how to use the TextCrawler with database storage."""
    
    # Initialize the crawler with database enabled
    crawler = TextCrawler(
        delay=1.0,           # 1 second delay between requests
        max_pages=10,        # Crawl up to 10 pages
        use_database=True    # Enable database storage
    )
    
    # Define starting URLs
    start_urls = [
        'https://portfolio-beige-ten-56.vercel.app/',
    ]
    
    print("Starting crawler with database integration...")
    print(f"Starting URLs: {start_urls}")
    print(f"Max pages: {crawler.max_pages}")
    print(f"Delay: {crawler.delay} seconds")
    print(f"Database enabled: {crawler.use_database}")
    print("-" * 50)
    
    # Start crawling
    results = crawler.crawl(start_urls)
    
    # Print results
    print(f"\nCrawling completed!")
    print(f"Pages crawled: {len(results)}")
    
    # Show some sample data
    for i, data in enumerate(results[:3]):  # Show first 3 results
        print(f"\n--- Page {i+1} ---")
        print(f"URL: {data['url']}")
        print(f"Title: {data['title']}")
        print(f"Text length: {len(data['text'])} characters")
        print(f"Status: {data['status_code']}")
    
    # Save results to files (optional, for backup)
    crawler.save_to_file('crawled_data.txt', format='txt')
    crawler.save_to_file('crawled_data.json', format='json')
    
    # Show statistics
    stats = crawler.get_stats()
    print(f"\n--- Statistics ---")
    print(f"Pages crawled: {stats['pages_crawled']}")
    print(f"URLs visited: {stats['urls_visited']}")
    print(f"Data collected: {stats['data_collected']}")
    
    # Show database statistics if available
    if 'total_pages' in stats:
        print(f"Total pages in database: {stats['total_pages']}")
        print(f"Total content length: {stats['total_content_length']} bytes")
        print(f"Average content length: {stats['average_content_length']:.2f} bytes")
    
    # Demonstrate database queries
    if crawler.use_database:
        print(f"\n--- Database Query Examples ---")
        try:
            db = next(get_db())
            
            # Get recent pages from database
            recent_pages = get_crawled_pages(db, limit=5)
            print(f"Recent 5 pages from database:")
            for page in recent_pages:
                print(f"  - {page.url} (ID: {page.id})")
            
            # Get database stats
            db_stats = get_db_stats(db)
            print(f"\nDatabase statistics:")
            print(f"  Total pages: {db_stats['total_pages']}")
            print(f"  Total content: {db_stats['total_content_length']} bytes")
            
        except Exception as e:
            print(f"Error querying database: {e}")


if __name__ == "__main__":
    main() 