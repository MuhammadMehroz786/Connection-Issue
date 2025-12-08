# Docker Deployment Guide

## 🐳 Quick Start

### Local Development with Docker

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Access the application:**
```
http://localhost:5000
```

3. **Stop the application:**
```bash
docker-compose down
```

---

## 🚀 Production Deployment

### Build Docker Image

```bash
docker build -t shopify-automation:latest .
```

### Run Container

```bash
docker run -d \
  -p 5000:5000 \
  -e PORT=5000 \
  -e SECRET_KEY=your-secret-key \
  -e FIRECRAWL_API_KEY=your-key \
  -e SHOPIFY_SHOP_URL=your-shop-url \
  -e SHOPIFY_ACCESS_TOKEN=your-token \
  -e OPENAI_API_KEY=your-key \
  -e SEEDREAM_API_KEY=your-key \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -v /path/to/data:/data \
  --name shopify-automation \
  shopify-automation:latest
```

---

## 🌐 Railway Deployment

Railway automatically detects the Dockerfile and builds your app.

### Steps:

1. **Push to GitHub**
2. **Connect to Railway**
3. **Add Environment Variables:**
   - `FIRECRAWL_API_KEY`
   - `SHOPIFY_SHOP_URL`
   - `SHOPIFY_ACCESS_TOKEN`
   - `OPENAI_API_KEY`
   - `SEEDREAM_API_KEY`
   - `SECRET_KEY`
   - Railway provides `DATABASE_URL` automatically

4. **Deploy** - Railway builds and deploys automatically

---

## 📦 Environment Variables

### Required:
- `FIRECRAWL_API_KEY` - Firecrawl API key
- `SHOPIFY_SHOP_URL` - Your Shopify store URL
- `SHOPIFY_ACCESS_TOKEN` - Shopify access token
- `OPENAI_API_KEY` - OpenAI API key
- `SEEDREAM_API_KEY` - SeeDream API key
- `SECRET_KEY` - Flask secret key

### Optional:
- `PORT` - Port to run on (default: 5000)
- `DATABASE_URL` - PostgreSQL connection string (uses SQLite if not set)
- `FLASK_DEBUG` - Debug mode (default: False)
- `PARALLEL_WORKERS` - Number of parallel workers (default: 2)
- `GEMINI_DELAY` - Delay after Gemini calls (default: 1.0)
- `OPENAI_DELAY` - Delay after OpenAI calls (default: 0.5)
- `SHOPIFY_DELAY` - Delay after Shopify calls (default: 0.6)

---

## 🗄️ Database

### SQLite (Default - Local Development)
- Database stored in `/data/shopify_automation.db`
- Mount volume: `-v ./data:/data`

### PostgreSQL (Production)
- Set `DATABASE_URL` environment variable
- Railway provides this automatically
- Format: `postgresql://user:password@host:port/database`

---

## 🔧 Docker Configuration

### Dockerfile Features:
- ✅ Python 3.11 slim base image
- ✅ Multi-stage caching for faster builds
- ✅ Gunicorn with 4 workers + 2 threads
- ✅ Health checks
- ✅ Optimized for production

### Resource Limits:
```bash
docker run -d \
  --memory="2g" \
  --cpus="2" \
  -p 5000:5000 \
  shopify-automation:latest
```

---

## 🐛 Troubleshooting

### Check logs:
```bash
docker logs shopify-automation
```

### Access container shell:
```bash
docker exec -it shopify-automation /bin/bash
```

### Rebuild without cache:
```bash
docker build --no-cache -t shopify-automation:latest .
```

### Check health:
```bash
docker inspect --format='{{.State.Health.Status}}' shopify-automation
```

---

## 📊 Performance

### Recommended Resources:
- **Memory**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 10GB minimum (for database and images)

### Gunicorn Configuration:
- Workers: 4 (adjust based on CPU cores)
- Threads: 2 per worker
- Timeout: 300 seconds (for long-running AI tasks)
- Keep-alive: 5 seconds

---

## 🔐 Security

1. **Never commit .env file**
2. **Use strong SECRET_KEY**
3. **Rotate API keys regularly**
4. **Use HTTPS in production**
5. **Keep dependencies updated**

---

## 📝 Notes

- Database migrations run automatically on startup
- Sessions stored in database (no cookie size limits)
- Supports both SQLite and PostgreSQL
- Health checks ensure container is running properly
- Logs output to stdout/stderr for easy monitoring
