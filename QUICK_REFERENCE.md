# 🔥 Firecrawl Integration - Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to `.env`:
```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

Get API key: https://firecrawl.dev

## Usage

### Web Interface

1. Go to http://localhost:5000/scrape
2. Choose method:
   - **🔥 Firecrawl** - Any e-commerce website
   - **📥 Apify** - Shopify stores only
3. Enter URL and click start
4. Review products at http://localhost:5000/products
5. Push to Shopify

### API

```bash
# Firecrawl (any website)
curl -X POST http://localhost:5000/api/scrape-firecrawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 100}'

# Apify (Shopify only)
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://store.myshopify.com", "max_products": 200}'
```

## When to Use Which?

| Firecrawl 🔥 | Apify 📥 |
|-------------|---------|
| WooCommerce | Shopify |
| Magento | |
| Custom stores | |
| Any e-commerce | |

## Files Added

- `services/firecrawl_service.py` - Firecrawl API
- `services/product_extractor.py` - OpenAI extraction
- `FIRECRAWL_GUIDE.md` - Full docs
- `FIRECRAWL_QUICKSTART.md` - Quick start
- `INTEGRATION_SUMMARY.md` - Technical details

## Files Modified

- `app.py` - Added Firecrawl workflow
- `requirements.txt` - Added firecrawl-py
- `.env.example` - Added FIRECRAWL_API_KEY
- `templates/scrape.html` - Added UI option

## Environment Variables

### Required
```env
FIRECRAWL_API_KEY=xxx        # NEW - For any website
SHOPIFY_SHOP_URL=xxx         # Your Shopify store
SHOPIFY_ACCESS_TOKEN=xxx     # Shopify API token
OPENAI_API_KEY=xxx           # For product extraction
GOOGLE_API_KEY=xxx           # For AI images
```

### Optional
```env
APIFY_API_TOKEN=xxx          # Only for Shopify scraping
```

## Workflow

```
Firecrawl crawls website
    ↓
OpenAI identifies product pages
    ↓
OpenAI extracts product data
    ↓
Save to database (Shopify format)
    ↓
Review in Products page
    ↓
Push to Shopify
```

## Cost (Example)

**100 pages, 20 products:**
- Firecrawl: ~$3.00
- OpenAI: ~$0.03
- Total: ~$3.03

**Apify (200 Shopify products):**
- Total: ~$0.50 - $2.00

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid API key | Check `.env` file |
| No products found | Try different website |
| Crawl failed | Reduce max_pages |
| Slow extraction | Normal (AI processing) |

## Support

- Full docs: `FIRECRAWL_GUIDE.md`
- Quick start: `FIRECRAWL_QUICKSTART.md`
- Technical: `INTEGRATION_SUMMARY.md`
- Original: `README.md`

## Testing

```bash
# 1. Start app
python app.py

# 2. Open browser
http://localhost:5000

# 3. Login
Username: Mahad
Password: Mahad

# 4. Go to Scrape page
# 5. Select Firecrawl
# 6. Enter: https://example-store.com
# 7. Max pages: 10 (for testing)
# 8. Click Start
# 9. Wait 2-5 minutes
# 10. Check Products page
```

## Key Features

✅ Crawl ANY e-commerce website
✅ AI-powered product detection
✅ Automatic data extraction
✅ Shopify-compatible format
✅ Same review workflow
✅ Backward compatible

## Next Steps

1. Install dependencies
2. Add Firecrawl API key
3. Test with small website
4. Review extracted products
5. Push to Shopify
6. Scale up!

---

**Quick Reference v1.0**
