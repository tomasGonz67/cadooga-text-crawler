"""
FastAPI application for the text crawler with health checks
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import logging
from datetime import datetime
import os

from crawler import TextCrawler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Text Crawler API",
    description="A FastAPI service for the text crawler with health monitoring",
    version="1.0.0"
)

# Global variables to track crawler state
crawler_status = {
    "is_running": False,
    "start_time": None,
    "end_time": None,
    "pages_crawled": 0,
    "errors": [],
    "last_activity": None
}

# Initialize crawler instance
crawler = None

class CrawlRequest(BaseModel):
    urls: List[str]
    max_pages: int = 10
    delay: float = 1.0

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: float
    version: str
    crawler_status: Dict

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Text Crawler API is running", "version": "1.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - (crawler_status.get("start_time", time.time()))
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime=uptime,
        version="1.0.0",
        crawler_status=crawler_status
    )

@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    # Check if the service is ready to accept requests
    ready = True
    status = "ready"
    
    # Add any readiness checks here
    # For example, check if crawler is not stuck in a long-running task
    
    if not ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": status, "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def get_status():
    """Get detailed crawler status"""
    return {
        "crawler_status": crawler_status,
        "system_info": {
            "python_version": os.sys.version,
            "platform": os.name,
            "current_time": datetime.now().isoformat()
        }
    }

@app.post("/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Start a new crawling job"""
    global crawler, crawler_status
    
    if crawler_status["is_running"]:
        raise HTTPException(status_code=409, detail="Crawler is already running")
    
    # Initialize crawler
    crawler = TextCrawler(delay=request.delay, max_pages=request.max_pages)
    
    # Update status
    crawler_status.update({
        "is_running": True,
        "start_time": time.time(),
        "end_time": None,
        "pages_crawled": 0,
        "errors": [],
        "last_activity": datetime.now().isoformat()
    })
    
    # Start crawling in background
    background_tasks.add_task(run_crawler, request.urls)
    
    return {
        "message": "Crawling started",
        "job_id": int(time.time()),
        "urls": request.urls,
        "max_pages": request.max_pages,
        "delay": request.delay
    }

@app.post("/crawl/stop")
async def stop_crawl():
    """Stop the current crawling job"""
    global crawler_status
    
    if not crawler_status["is_running"]:
        raise HTTPException(status_code=409, detail="No crawler is running")
    
    crawler_status.update({
        "is_running": False,
        "end_time": time.time(),
        "last_activity": datetime.now().isoformat()
    })
    
    return {"message": "Crawling stopped", "timestamp": datetime.now().isoformat()}

@app.get("/crawl/results")
async def get_results():
    """Get crawling results"""
    global crawler
    
    if not crawler:
        raise HTTPException(status_code=404, detail="No crawler instance found")
    
    stats = crawler.get_stats()
    
    return {
        "stats": stats,
        "data_count": len(crawler.crawled_data),
        "sample_data": crawler.crawled_data[:3] if crawler.crawled_data else []
    }

async def run_crawler(urls: List[str]):
    """Background task to run the crawler"""
    global crawler, crawler_status
    
    try:
        logger.info(f"Starting crawler with URLs: {urls}")
        
        # Run the crawler
        results = crawler.crawl(urls)
        
        # Update status
        crawler_status.update({
            "is_running": False,
            "end_time": time.time(),
            "pages_crawled": len(results),
            "last_activity": datetime.now().isoformat()
        })
        
        # Save results
        if results:
            crawler.save_to_file('output/crawled_data.txt', format='txt')
            crawler.save_to_file('output/crawled_data.json', format='json')
        
        logger.info(f"Crawling completed. Processed {len(results)} pages.")
        
    except Exception as e:
        logger.error(f"Error during crawling: {e}")
        crawler_status.update({
            "is_running": False,
            "end_time": time.time(),
            "errors": crawler_status.get("errors", []) + [str(e)],
            "last_activity": datetime.now().isoformat()
        })

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 