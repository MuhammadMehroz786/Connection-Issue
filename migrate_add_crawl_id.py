"""
Migration: Add crawl_id column to scrape_jobs table
This allows tracking and cancelling Firecrawl crawls
"""

from app import app, db
from models import ScrapeJob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add crawl_id column to scrape_jobs table"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('scrape_jobs')]
            
            if 'crawl_id' in columns:
                logger.info("✅ crawl_id column already exists in scrape_jobs table")
                return
            
            # Add the column
            logger.info("Adding crawl_id column to scrape_jobs table...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE scrape_jobs ADD COLUMN crawl_id VARCHAR(100)'))
                conn.commit()
            
            logger.info("✅ Successfully added crawl_id column to scrape_jobs table")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
