"""
Database models and connection setup for the text crawler
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://crawler_user:crawler_password@localhost:5432/text_crawler_db'
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class CrawledPage(Base):
    """Model for storing crawled page data."""
    
    __tablename__ = "crawled_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    content_length = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_url_created_at', 'url', 'created_at'),
        Index('idx_created_at', 'created_at'),
    )


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def save_crawled_data(data: dict, db_session) -> CrawledPage:
    """
    Save crawled data to database.
    
    Args:
        data: Dictionary containing crawled page data
        db_session: Database session
        
    Returns:
        CrawledPage instance
    """
    # Check if URL already exists
    existing_page = db_session.query(CrawledPage).filter(
        CrawledPage.url == data['url']
    ).first()
    
    if existing_page:
        # Update existing record
        existing_page.title = data.get('title', existing_page.title)
        existing_page.description = data.get('description', existing_page.description)
        existing_page.text_content = data.get('text', existing_page.text_content)
        existing_page.html_content = data.get('html', existing_page.html_content)
        existing_page.status_code = data.get('status_code', existing_page.status_code)
        existing_page.content_length = data.get('content_length', existing_page.content_length)
        db_session.commit()
        return existing_page
    else:
        # Create new record
        crawled_page = CrawledPage(
            url=data['url'],
            title=data.get('title', ''),
            description=data.get('description', ''),
            text_content=data.get('text', ''),
            html_content=data.get('html', ''),
            status_code=data.get('status_code'),
            content_length=data.get('content_length')
        )
        db_session.add(crawled_page)
        db_session.commit()
        db_session.refresh(crawled_page)
        return crawled_page


def get_crawled_pages(db_session, limit: Optional[int] = None, offset: int = 0):
    """
    Get crawled pages from database.
    
    Args:
        db_session: Database session
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of CrawledPage instances
    """
    query = db_session.query(CrawledPage).order_by(CrawledPage.created_at.desc())
    
    if offset:
        query = query.offset(offset)
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def get_page_by_url(db_session, url: str) -> Optional[CrawledPage]:
    """
    Get a specific page by URL.
    
    Args:
        db_session: Database session
        url: URL to search for
        
    Returns:
        CrawledPage instance or None if not found
    """
    return db_session.query(CrawledPage).filter(CrawledPage.url == url).first()


def get_stats(db_session) -> dict:
    """
    Get crawling statistics from database.
    
    Args:
        db_session: Database session
        
    Returns:
        Dictionary with statistics
    """
    total_pages = db_session.query(CrawledPage).count()
    total_content_length = db_session.query(func.sum(CrawledPage.content_length)).scalar() or 0
    
    return {
        'total_pages': total_pages,
        'total_content_length': total_content_length,
        'average_content_length': total_content_length / total_pages if total_pages > 0 else 0
    } 