"""
Database management utilities for the text crawler
"""

import argparse
from database import init_db, get_db, get_crawled_pages, get_stats, get_page_by_url
from sqlalchemy import text


def init_database():
    """Initialize the database tables."""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


def show_stats():
    """Show database statistics."""
    try:
        db = next(get_db())
        stats = get_stats(db)
        
        print("=== Database Statistics ===")
        print(f"Total pages: {stats['total_pages']}")
        print(f"Total content length: {stats['total_content_length']} bytes")
        print(f"Average content length: {stats['average_content_length']:.2f} bytes")
        
    except Exception as e:
        print(f"Error getting stats: {e}")


def list_pages(limit=10, offset=0):
    """List crawled pages."""
    try:
        db = next(get_db())
        pages = get_crawled_pages(db, limit=limit, offset=offset)
        
        print(f"=== Recent {len(pages)} Pages ===")
        for page in pages:
            print(f"ID: {page.id}")
            print(f"URL: {page.url}")
            print(f"Title: {page.title[:100]}...")
            print(f"Created: {page.created_at}")
            print(f"Content length: {page.content_length} bytes")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error listing pages: {e}")


def search_pages(query):
    """Search pages by URL."""
    try:
        db = next(get_db())
        pages = db.execute(
            text("SELECT * FROM crawled_pages WHERE url ILIKE :query ORDER BY created_at DESC"),
            {"query": f"%{query}%"}
        ).fetchall()
        
        print(f"=== Search Results for '{query}' ===")
        for page in pages:
            print(f"ID: {page.id}")
            print(f"URL: {page.url}")
            print(f"Title: {page.title[:100]}...")
            print(f"Created: {page.created_at}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error searching pages: {e}")


def clear_database():
    """Clear all data from the database."""
    try:
        db = next(get_db())
        db.execute(text("DELETE FROM crawled_pages"))
        db.commit()
        print("Database cleared successfully!")
        
    except Exception as e:
        print(f"Error clearing database: {e}")


def main():
    parser = argparse.ArgumentParser(description="Database management for text crawler")
    parser.add_argument("command", choices=["init", "stats", "list", "search", "clear"], 
                       help="Command to execute")
    parser.add_argument("--limit", type=int, default=10, help="Limit for list command")
    parser.add_argument("--offset", type=int, default=0, help="Offset for list command")
    parser.add_argument("--query", type=str, help="Search query for search command")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_database()
    elif args.command == "stats":
        show_stats()
    elif args.command == "list":
        list_pages(limit=args.limit, offset=args.offset)
    elif args.command == "search":
        if not args.query:
            print("Error: --query is required for search command")
            return
        search_pages(args.query)
    elif args.command == "clear":
        confirm = input("Are you sure you want to clear all data? (yes/no): ")
        if confirm.lower() == "yes":
            clear_database()
        else:
            print("Operation cancelled.")


if __name__ == "__main__":
    main() 