"""
Example usage of the basic text crawler
"""

from crawler import TextCrawler


def main():
    """Example of how to use the TextCrawler."""
    
    # Initialize the crawler
    crawler = TextCrawler(
        delay=1.0,      # 1 second delay between requests
        max_pages=10    # Crawl up to 10 pages
    )
    
    # Define starting URLs
    start_urls = [
        'https://portfolio-beige-ten-56.vercel.app/',
    ]
    
    print("Starting crawler...")
    print(f"Starting URLs: {start_urls}")
    print(f"Max pages: {crawler.max_pages}")
    print(f"Delay: {crawler.delay} seconds")
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
    
    # Save results
    crawler.save_to_file('crawled_data.txt', format='txt')
    crawler.save_to_file('crawled_data.json', format='json')
    
    # Show statistics
    stats = crawler.get_stats()
    print(f"\n--- Statistics ---")
    print(f"Pages crawled: {stats['pages_crawled']}")
    print(f"URLs visited: {stats['urls_visited']}")
    print(f"Data collected: {stats['data_collected']}")


if __name__ == "__main__":
    main() 