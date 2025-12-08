# 🔥 Firecrawl Integration Guide

## Overview

This application now supports crawling **ANY e-commerce website** (not just Shopify) using Firecrawl and OpenAI for intelligent product extraction.

## How It Works

### 1. Firecrawl Crawls the Website
- Crawls any e-commerce website (WooCommerce, Magento, custom stores, etc.)
- Extracts page content in markdown and HTML format
- Respects robots.txt and excludes non-product pages (cart, checkout, etc.)

### 2. OpenAI Identifies Product Pages
- Analyzes each crawled page to determine if it's a product page
- Uses heuristics + AI for accurate detection
- Filters out category pages, blog posts, and other non-product content

### 3. OpenAI Extracts Structured Data
- Extracts product information in Shopify-compatible format:
  - Title
  - Description (formatted as HTML)
  - Price and compare-at price
  - Variants (size, color, etc.)
  - Images
  - SKU, vendor, product type
  - Tags

### 4. Save to Database
- Products are saved in the same database format as Apify products
- You can review, edit, and push them to Shopify

## Setup

### 1. Get Firecrawl API Key

1. Sign up at [Firecrawl.dev](https://firecrawl.dev)
2. Get your API key from the dashboard
3. Add it to your `.env` file:

```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The `firecrawl-py` package is now included in requirements.txt.

### 3. Configure OpenAI

Make sure you have your OpenAI API key configured (already required for AI features):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### From the Web Interface

1. Go to the **Scrape** page
2. Click **"🔥 Firecrawl (Any Website)"** button
3. Enter the e-commerce website URL (e.g., `https://example.com`)
4. Set max pages to crawl (default: 100)
5. Click **"Start Firecrawl + AI Extraction"**
6. Wait for the crawl to complete (may take a few minutes)
7. Review products in the **Products** page
8. Push selected products to Shopify

### From the API

```bash
curl -X POST http://localhost:5000/api/scrape-firecrawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_pages": 100
  }'
```

## Comparison: Firecrawl vs Apify

| Feature | Firecrawl | Apify |
|---------|-----------|-------|
| **Supported Sites** | Any e-commerce website | Shopify only |
| **Product Detection** | AI-powered (OpenAI) | Built-in Shopify scraper |
| **Data Extraction** | AI-powered (OpenAI) | Native Shopify data |
| **Speed** | Slower (AI processing) | Faster (direct API) |
| **Accuracy** | High (AI understands context) | Very high (native data) |
| **Cost** | Firecrawl + OpenAI credits | Apify credits only |
| **Best For** | Non-Shopify sites | Shopify stores |

## Configuration

### Environment Variables

```env
# Required for Firecrawl
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for Shopify-specific scraping)
APIFY_API_TOKEN=your_apify_token_here
```

### Crawl Settings

You can adjust crawl settings in `services/firecrawl_service.py`:

```python
payload = {
    "url": website_url,
    "limit": max_pages,  # Max pages to crawl
    "scrapeOptions": {
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
        "waitFor": 2000  # Wait for dynamic content (ms)
    },
    "excludePaths": [
        "**/cart",
        "**/checkout",
        "**/account",
        # Add more paths to exclude
    ]
}
```

### OpenAI Model

The product extractor uses `gpt-4o-mini` by default (fast and cost-effective). You can change this in `services/product_extractor.py`:

```python
self.model = "gpt-4o-mini"  # or "gpt-4o" for better accuracy
```

## Workflow

### Firecrawl Workflow

```
1. User enters website URL
   ↓
2. Firecrawl crawls website (up to max_pages)
   ↓
3. For each crawled page:
   - Check if it's a product page (heuristics + OpenAI)
   - If yes, extract product data with OpenAI
   ↓
4. Save extracted products to database
   ↓
5. User reviews products in Products page
   ↓
6. User pushes selected products to Shopify
```

### Apify Workflow (Shopify Only)

```
1. User enters Shopify store URL
   ↓
2. Apify scrapes Shopify store
   ↓
3. Products saved to database
   ↓
4. User reviews products in Products page
   ↓
5. User pushes selected products to Shopify
```

## Troubleshooting

### Firecrawl API Errors

**Error: "Invalid API key"**
- Check that `FIRECRAWL_API_KEY` is set correctly in `.env`
- Make sure there are no extra spaces or quotes

**Error: "Crawl failed or timed out"**
- The website may be blocking crawlers
- Try reducing `max_pages`
- Check if the website is accessible

### OpenAI Extraction Errors

**Error: "No products extracted"**
- The website may not have product pages
- Try a different website
- Check OpenAI API key and credits

**Error: "Failed to parse JSON"**
- OpenAI response was malformed
- This is rare - try again or check OpenAI status

### No Products Found

If Firecrawl completes but no products are found:

1. **Check the website structure**
   - Make sure it's an e-commerce site with product pages
   - Some sites may use JavaScript-heavy rendering

2. **Adjust detection heuristics**
   - Edit `services/product_extractor.py`
   - Modify `product_indicators` list

3. **Increase max_pages**
   - Some sites have products deep in the site structure

## Cost Estimation

### Firecrawl Costs
- Approximately $0.01 - $0.05 per page crawled
- 100 pages = $1 - $5

### OpenAI Costs (gpt-4o-mini)
- Product detection: ~$0.0001 per page
- Product extraction: ~$0.001 per product
- 100 pages with 20 products = ~$0.03

### Total Cost Example
- Crawl 100 pages, extract 20 products
- Firecrawl: ~$3
- OpenAI: ~$0.03
- **Total: ~$3.03**

Compare to Apify (Shopify only):
- 200 products: ~$0.50 - $2.00

## Best Practices

1. **Start small**: Test with `max_pages: 10` first
2. **Use Apify for Shopify**: It's faster and cheaper for Shopify stores
3. **Use Firecrawl for everything else**: WooCommerce, Magento, custom stores
4. **Review before pushing**: Always review extracted products before pushing to Shopify
5. **Monitor costs**: Keep an eye on Firecrawl and OpenAI usage

## API Reference

### POST /api/scrape-firecrawl

Start a Firecrawl crawl and product extraction job.

**Request:**
```json
{
  "url": "https://example.com",
  "max_pages": 100
}
```

**Response:**
```json
{
  "message": "Firecrawl scraping started successfully",
  "task_id": "task_abc123",
  "job_id": 42,
  "status": "processing"
}
```

### GET /api/jobs/<task_id>

Get the status of a scraping job (works for both Firecrawl and Apify).

**Response:**
```json
{
  "id": 42,
  "task_id": "task_abc123",
  "source_url": "https://example.com",
  "status": "completed",
  "total_products": 25,
  "products_processed": 25,
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:05:00"
}
```

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify API keys are correct
3. Test with a simple e-commerce website first
4. Check Firecrawl and OpenAI status pages

## Future Enhancements

Potential improvements:
- [ ] Support for more e-commerce platforms (Shopify, WooCommerce, Magento detection)
- [ ] Batch processing for large websites
- [ ] Custom extraction rules per website
- [ ] Image downloading and hosting
- [ ] Automatic price conversion
- [ ] Multi-language support

---

**Made with ❤️ for universal e-commerce scraping**
