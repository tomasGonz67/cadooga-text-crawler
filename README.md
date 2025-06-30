# Cadooga Text Crawler with PostgreSQL Database

A web crawler that extracts text content from websites and stores it in a PostgreSQL database.

## Features

- **Web Crawling**: Crawls websites and extracts text content, titles, descriptions, and HTML
- **Database Storage**: Stores crawled data in PostgreSQL with proper indexing
- **File Export**: Still supports exporting to TXT and JSON files
- **Docker Support**: Complete Docker setup with PostgreSQL
- **Database Management**: Tools for managing and querying the database

## Quick Start

### Using Docker (Recommended)

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Initialize the database**:
   ```bash
   docker-compose exec text-crawler-api python db_manager.py init
   ```

3. **Run the crawler**:
   ```bash
   docker-compose exec text-crawler-api python example.py
   ```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL**:
   - Install PostgreSQL
   - Create database: `text_crawler_db`
   - Create user: `crawler_user` with password: `crawler_password`
   - Or use Docker: `docker run --name postgres -e POSTGRES_DB=text_crawler_db -e POSTGRES_USER=crawler_user -e POSTGRES_PASSWORD=crawler_password -p 5432:5432 -d postgres:15`

3. **Initialize database**:
   ```bash
   python db_manager.py init
   ```

4. **Run the crawler**:
   ```bash
   python example.py
   ```

## Database Schema

The crawler stores data in the `crawled_pages` table:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| url | String(2048) | The crawled URL |
| title | String(500) | Page title |
| description | Text | Meta description |
| text_content | Text | Extracted text content |
| html_content | Text | Full HTML content |
| status_code | Integer | HTTP status code |
| content_length | Integer | Content length in bytes |
| created_at | DateTime | When the page was crawled |
| updated_at | DateTime | When the page was last updated |

## Usage

### Basic Crawling

```python
from crawler import TextCrawler

# Initialize crawler with database enabled
crawler = TextCrawler(
    delay=1.0,           # Delay between requests
    max_pages=10,        # Maximum pages to crawl
    use_database=True    # Enable database storage
)

# Start crawling
results = crawler.crawl(['https://example.com'])

# Save to files (optional)
crawler.save_to_file('output.txt', format='txt')
crawler.save_to_file('output.json', format='json')
```

### Database Operations

```python
from database import get_db, get_crawled_pages, get_stats

# Get database session
db = next(get_db())

# Get recent pages
pages = get_crawled_pages(db, limit=10)

# Get statistics
stats = get_stats(db)
print(f"Total pages: {stats['total_pages']}")
```

### Database Management

Use the `db_manager.py` script for database operations:

```bash
# Initialize database
python db_manager.py init

# Show statistics
python db_manager.py stats

# List recent pages
python db_manager.py list --limit 20

# Search pages
python db_manager.py search --query "example.com"

# Clear all data
python db_manager.py clear
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://crawler_user:crawler_password@localhost:5432/text_crawler_db`)

### Docker Environment

The Docker setup automatically configures:
- PostgreSQL database on port 5432
- Database name: `text_crawler_db`
- Username: `crawler_user`
- Password: `crawler_password`

## API Integration

The crawler can be integrated with the existing FastAPI (`api.py`) by:

1. Adding database endpoints to the API
2. Using the database functions in API routes
3. Exposing database statistics and queries via REST endpoints

## Performance Considerations

- **Indexing**: The database includes indexes on `url` and `created_at` for better query performance
- **Content Storage**: Large HTML content is stored as TEXT, consider compression for very large sites
- **Batch Operations**: For large-scale crawling, consider batch inserts for better performance

## Troubleshooting

### Database Connection Issues

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

3. Test connection:
   ```bash
   docker-compose exec postgres psql -U crawler_user -d text_crawler_db
   ```

### Memory Issues

For large-scale crawling:
- Increase Docker memory limits
- Consider using database connection pooling
- Implement pagination for large result sets

## Development

### Adding New Features

1. **New Database Fields**: Update the `CrawledPage` model in `database.py`
2. **New Crawler Features**: Extend the `TextCrawler` class in `crawler.py`
3. **API Endpoints**: Add new routes to `api.py`

### Testing

```bash
# Run crawler with test URLs
python example.py

# Check database contents
python db_manager.py stats
python db_manager.py list --limit 5
```

## License

This project is part of the Cadooga text crawler system. 