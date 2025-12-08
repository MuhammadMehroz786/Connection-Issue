# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository with your code

### Step 1: Create New Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect it's a Python app

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically:
   - Create a PostgreSQL database
   - Set the `DATABASE_URL` environment variable
   - Connect it to your app

### Step 3: Configure Environment Variables

In Railway dashboard, go to your app → **Variables** tab and add:

```env
# Required
FIRECRAWL_API_KEY=your_firecrawl_api_key
SHOPIFY_SHOP_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_token
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key

# Optional (Railway sets these automatically)
PORT=${{PORT}}
DATABASE_URL=${{DATABASE_URL}}

# Security
SECRET_KEY=generate-a-random-secret-key-here
FLASK_DEBUG=False
```

### Step 4: Deploy

1. Railway will automatically deploy on every git push
2. First deployment takes ~5 minutes
3. You'll get a URL like: `https://your-app.up.railway.app`

### Step 5: Initialize Database

The database tables are created automatically on first run. No manual migration needed!

## Database Behavior

### Local Development (SQLite)
```
✅ Uses SQLite automatically
✅ Database file: shopify_automation.db
✅ No configuration needed
```

### Railway Production (PostgreSQL)
```
✅ Detects DATABASE_URL automatically
✅ Uses PostgreSQL for better performance
✅ Handles concurrent requests
✅ Persistent across deployments
```

## Monitoring

### Check Logs
```bash
# In Railway dashboard
Click your app → "Deployments" → "View Logs"
```

### Database Connection
The app logs will show:
- Local: `📁 Using local SQLite database`
- Railway: `🐘 Using PostgreSQL database (production mode)`

## Scaling

### Vertical Scaling (More Power)
- Railway automatically scales based on usage
- Upgrade plan for more resources

### Horizontal Scaling (Multiple Instances)
- PostgreSQL handles concurrent connections
- App is stateless (can run multiple instances)

## Troubleshooting

### Database Connection Issues

**Problem**: `DATABASE_URL` not found
```bash
# Solution: Make sure PostgreSQL service is added
Railway Dashboard → + New → Database → PostgreSQL
```

**Problem**: Connection timeout
```bash
# Solution: Check PostgreSQL service is running
Railway Dashboard → PostgreSQL → Check status
```

### Migration from SQLite to PostgreSQL

If you have local SQLite data you want to migrate:

1. **Export from SQLite**:
```bash
sqlite3 shopify_automation.db .dump > backup.sql
```

2. **Import to PostgreSQL**:
```bash
# Get PostgreSQL connection string from Railway
psql $DATABASE_URL < backup.sql
```

Or use a tool like [pgloader](https://pgloader.io/)

## Environment Variables Reference

### Required for Production
| Variable | Description | Example |
|----------|-------------|---------|
| `FIRECRAWL_API_KEY` | Firecrawl API key | `fc_xxx...` |
| `SHOPIFY_SHOP_URL` | Your Shopify store | `https://store.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Shopify API token | `shpat_xxx...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-xxx...` |
| `GOOGLE_API_KEY` | Google Gemini key | `AIza...` |
| `SECRET_KEY` | Flask secret key | Random string |

### Auto-Provided by Railway
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `PORT` | Port to run the app |

### Optional Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `False` | Debug mode (keep False in production) |
| `PARALLEL_WORKERS` | `4` | Number of parallel AI workers |
| `GEMINI_DELAY` | `0.3` | Delay between Gemini API calls |
| `OPENAI_DELAY` | `0.3` | Delay between OpenAI API calls |
| `SHOPIFY_DELAY` | `0.6` | Delay between Shopify API calls |

## Performance Tips

### 1. Use PostgreSQL Connection Pooling
Already configured! The app uses:
- Pool size: 20 connections
- Max overflow: 10 connections
- Connection recycling: 300 seconds

### 2. Monitor API Usage
- Firecrawl: ~$3 per 100 pages
- OpenAI: ~$0.03 per 100 products
- Gemini: ~$0.10 per 100 images

### 3. Optimize Batch Sizes
Current settings (optimized for Railway):
- Page processing: 50 pages per batch
- Product grouping: Indexed (O(n) complexity)

## Cost Estimation

### Railway Costs
- **Hobby Plan**: $5/month
  - 500 hours execution time
  - 512MB RAM
  - PostgreSQL included

- **Pro Plan**: $20/month
  - Unlimited execution time
  - 8GB RAM
  - Better PostgreSQL performance

### API Costs (per 1000 products)
- Firecrawl: ~$30
- OpenAI: ~$0.30
- Gemini: ~$1.00
- **Total**: ~$31.30 per 1000 products

## Security Best Practices

1. **Never commit secrets**
   - Use Railway environment variables
   - Don't put API keys in code

2. **Use strong SECRET_KEY**
   ```python
   import secrets
   secrets.token_hex(32)
   ```

3. **Enable HTTPS**
   - Railway provides HTTPS automatically
   - All traffic is encrypted

4. **Rotate API keys regularly**
   - Update in Railway dashboard
   - App restarts automatically

## Support

### Railway Issues
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app

### App Issues
- Check logs in Railway dashboard
- Verify all environment variables are set
- Test locally first with SQLite

---

**Ready to deploy!** 🚀

Push your code to GitHub and connect it to Railway. The app will automatically detect PostgreSQL and configure itself.
