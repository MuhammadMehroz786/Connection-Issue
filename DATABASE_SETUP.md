# Database Setup Guide

## Automatic Database Detection

The app automatically detects and configures the appropriate database:

### 🏠 Local Development
```
✅ SQLite (automatic)
📁 File: shopify_automation.db
🔧 No configuration needed
```

### 🚂 Railway Production
```
✅ PostgreSQL (automatic)
🐘 Detects DATABASE_URL environment variable
🔧 No manual configuration needed
```

## How It Works

### Detection Logic
```python
if DATABASE_URL exists:
    → Use PostgreSQL (production)
else:
    → Use SQLite (local development)
```

### Configuration

**Local (.env file)**:
```env
# No DATABASE_URL = SQLite automatically
FIRECRAWL_API_KEY=xxx
SHOPIFY_SHOP_URL=xxx
# ... other variables
```

**Railway (Environment Variables)**:
```env
# Railway sets this automatically when you add PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/db

# Your variables
FIRECRAWL_API_KEY=xxx
SHOPIFY_SHOP_URL=xxx
# ... other variables
```

## Database Tables

Both SQLite and PostgreSQL use the same schema:

### Tables Created Automatically
- `scrape_jobs` - Scraping job tracking
- `products` - Product data
- `product_variants` - Product variants
- `product_images` - Product images
- `product_metafields` - Product metadata
- `ai_products` - AI-enhanced products
- `ai_product_variants` - AI product variants
- `ai_product_images` - AI product images
- `ai_jobs` - AI job tracking

### First Run
On first startup, the app automatically:
1. Detects database type
2. Creates all tables
3. Logs: `Database tables created successfully`

## Migration from SQLite to PostgreSQL

If you have local data you want to move to production:

### Option 1: Fresh Start (Recommended)
Just deploy to Railway with PostgreSQL. Start fresh.

### Option 2: Migrate Data
```bash
# 1. Export SQLite data
sqlite3 shopify_automation.db .dump > backup.sql

# 2. Clean up SQLite-specific syntax
sed 's/AUTOINCREMENT/SERIAL/g' backup.sql > postgres_backup.sql

# 3. Import to PostgreSQL (get URL from Railway)
psql $DATABASE_URL < postgres_backup.sql
```

### Option 3: Use pgloader
```bash
# Install pgloader
brew install pgloader  # macOS
apt-get install pgloader  # Linux

# Migrate
pgloader shopify_automation.db $DATABASE_URL
```

## Testing Database Connection

### Local (SQLite)
```bash
# Run the app
python app.py

# Check logs
# Should see: "📁 Using local SQLite database"

# Verify database file exists
ls -lh shopify_automation.db
```

### Railway (PostgreSQL)
```bash
# Check Railway logs
# Should see: "🐘 Using PostgreSQL database (production mode)"

# Test connection from Railway dashboard
Railway → PostgreSQL → "Connect" → "psql"
```

## Database Performance

### SQLite (Local)
- ✅ Perfect for development
- ✅ No setup required
- ✅ Single file
- ⚠️ Not for production (single connection)

### PostgreSQL (Production)
- ✅ Handles concurrent requests
- ✅ Better performance at scale
- ✅ ACID compliance
- ✅ Connection pooling (20 connections)
- ✅ Automatic backups (Railway)

## Troubleshooting

### SQLite Issues

**Problem**: Database locked
```bash
# Solution: Close other connections
# SQLite only allows one writer at a time
```

**Problem**: Database file not found
```bash
# Solution: Run the app once to create it
python app.py
```

### PostgreSQL Issues

**Problem**: Connection refused
```bash
# Solution: Check DATABASE_URL is set
echo $DATABASE_URL

# In Railway: Check PostgreSQL service is running
```

**Problem**: Too many connections
```bash
# Solution: Already configured with connection pooling
# Max 20 connections + 10 overflow = 30 total
```

**Problem**: SSL required
```bash
# Solution: Already handled automatically
# Railway PostgreSQL uses SSL by default
```

## Backup Strategy

### Local (SQLite)
```bash
# Simple file copy
cp shopify_automation.db shopify_automation.db.backup

# Or use SQLite backup
sqlite3 shopify_automation.db ".backup backup.db"
```

### Railway (PostgreSQL)
```bash
# Railway provides automatic daily backups
# Access from: Railway Dashboard → PostgreSQL → Backups

# Manual backup
pg_dump $DATABASE_URL > backup.sql
```

## Connection Strings

### SQLite Format
```
sqlite:///shopify_automation.db
sqlite:////absolute/path/to/database.db
```

### PostgreSQL Format
```
postgresql://user:password@host:5432/database
postgresql://user:password@host:5432/database?sslmode=require
```

## Environment Variables

### Required for PostgreSQL
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Optional
```env
DATABASE_PATH=/custom/path/database.db  # For SQLite only
```

## Summary

✅ **Local Development**: SQLite (automatic, no config)
✅ **Railway Production**: PostgreSQL (automatic, Railway provides DATABASE_URL)
✅ **Tables**: Created automatically on first run
✅ **Migration**: Optional, fresh start recommended
✅ **Backups**: Railway handles automatically

**No manual database setup required!** 🎉
