# 🔥 Firecrawl Quick Start

## What Changed?

Your Shopify automation bot can now crawl **ANY e-commerce website** (not just Shopify) using Firecrawl + OpenAI.

## Setup (2 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Firecrawl API Key to .env
```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

Get your API key from: https://firecrawl.dev

### 3. Run the App
```bash
python app.py
```

## How to Use

### Option 1: Firecrawl (Any Website) 🔥
1. Go to **Scrape** page
2. Click **"🔥 Firecrawl (Any Website)"**
3. Enter any e-commerce URL (e.g., `https://example.com`)
4. Click **"Start Firecrawl + AI Extraction"**
5. Wait for crawl to complete
6. Review products in **Products** page
7. Push to Shopify

### Option 2: Apify (Shopify Only) 📥
1. Go to **Scrape** page
2. Click **"📥 Apify (Shopify Only)"**
3. Enter Shopify store URL
4. Click **"Fetch Products from Last Run"**
5. Review and push to Shopify

## What Happens Behind the Scenes?

### Firecrawl Method
```
1. Firecrawl crawls the website (all pages)
2. OpenAI checks each page: "Is this a product page?"
3. If yes, OpenAI extracts: title, price, variants, images, description
4. Products saved to database in Shopify format
5. You review and push to your Shopify store
```

### Apify Method (Unchanged)
```
1. Apify scrapes Shopify store (native data)
2. Products saved to database
3. You review and push to your Shopify store
```

## When to Use Which?

| Use Firecrawl When | Use Apify When |
|-------------------|----------------|
| ✅ Non-Shopify sites | ✅ Shopify stores |
| ✅ WooCommerce | ✅ Need fast scraping |
| ✅ Magento | ✅ Want lowest cost |
| ✅ Custom stores | ✅ Need 100% accuracy |

## Cost Comparison

**Firecrawl (100 pages, 20 products)**
- Firecrawl: ~$3
- OpenAI: ~$0.03
- Total: ~$3.03

**Apify (200 products)**
- Apify: ~$0.50 - $2.00

## Files Changed

### New Files
- `services/firecrawl_service.py` - Firecrawl API integration
- `services/product_extractor.py` - OpenAI product extraction
- `FIRECRAWL_GUIDE.md` - Full documentation
- `FIRECRAWL_QUICKSTART.md` - This file

### Modified Files
- `app.py` - Added Firecrawl workflow and API endpoint
- `requirements.txt` - Added `firecrawl-py==1.5.1`
- `.env.example` - Added `FIRECRAWL_API_KEY`
- `templates/scrape.html` - Added Firecrawl UI option

### Unchanged
- All other functionality remains the same
- Database structure unchanged
- Shopify integration unchanged
- AI enhancement features unchanged

## Environment Variables

### Required (New)
```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### Required (Existing)
```env
SHOPIFY_SHOP_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_token
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```

### Optional (Existing)
```env
APIFY_API_TOKEN=your_apify_token  # Only needed for Shopify scraping
```

## Testing

### Test Firecrawl
```bash
# Start the app
python app.py

# In browser:
# 1. Go to http://localhost:5000
# 2. Login (Mahad/Mahad)
# 3. Click "Scrape"
# 4. Select "Firecrawl (Any Website)"
# 5. Enter: https://example-ecommerce-site.com
# 6. Click "Start Firecrawl + AI Extraction"
# 7. Wait 2-5 minutes
# 8. Check "Products" page
```

## Troubleshooting

**"Invalid API key"**
- Check `.env` file has `FIRECRAWL_API_KEY`
- No extra spaces or quotes

**"No products found"**
- Website may not have product pages
- Try a different site
- Increase `max_pages`

**"Crawl failed"**
- Website may block crawlers
- Check if site is accessible
- Try reducing `max_pages`

## Next Steps

1. ✅ Install dependencies
2. ✅ Add Firecrawl API key
3. ✅ Test with a small website (10 pages)
4. ✅ Review extracted products
5. ✅ Push to Shopify
6. 🎉 Scale up!

## Support

- Full docs: `FIRECRAWL_GUIDE.md`
- Original docs: `README.md`
- Setup guide: `SETUP_GUIDE.md`

---

**You can now scrape ANY e-commerce website! 🎉**
