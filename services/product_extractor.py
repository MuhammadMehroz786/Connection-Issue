"""
Product Extractor Service
Uses OpenAI to identify product pages and extract structured product data
"""

import logging
import json
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class ProductExtractorService:
    """Service for extracting product data from crawled pages using OpenAI"""

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"  # Fast and cost-effective

    def is_product_page(self, page_content: str, page_url: str) -> bool:
        """
        Determine if a page contains product information
        
        Args:
            page_content: The markdown/text content of the page
            page_url: The URL of the page
            
        Returns:
            True if it's a product page, False otherwise
        """
        # Quick heuristic checks first (faster than API call)
        content_lower = page_content.lower()
        url_lower = page_url.lower()
        
        # Strong indicators it's a product page
        product_indicators = [
            'add to cart', 'buy now', 'add to bag', 'purchase',
            'in stock', 'out of stock', 'price', '$', '£', '€',
            'quantity', 'size', 'color', 'variant'
        ]
        
        # Strong indicators it's NOT a product page
        non_product_indicators = [
            '/category/', '/collection/', '/search', '/blog/',
            'all products', 'shop all', 'view all'
        ]
        
        # Check if URL suggests it's NOT a product page
        if any(indicator in url_lower for indicator in non_product_indicators):
            return False
        
        # Check if content has product indicators
        indicator_count = sum(1 for indicator in product_indicators if indicator in content_lower)
        
        # If we have 3+ indicators, it's likely a product page
        if indicator_count >= 3:
            return True
        
        # If less than 2 indicators, probably not a product page
        if indicator_count < 2:
            return False
        
        # For borderline cases, use OpenAI (truncate content to save tokens)
        truncated_content = page_content[:2000]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product page detector. Respond with only 'YES' if the page is a product detail page (single product for sale), or 'NO' if it's a category/collection/listing page or non-product page."
                    },
                    {
                        "role": "user",
                        "content": f"URL: {page_url}\n\nContent:\n{truncated_content}\n\nIs this a product detail page?"
                    }
                ],
                temperature=0,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip().upper()
            return answer == "YES"
            
        except Exception as e:
            logger.error(f"Error checking if product page: {str(e)}")
            # Default to True if we had some indicators
            return indicator_count >= 2

    def extract_product_data(self, page_content: str, page_url: str) -> Optional[Dict]:
        """
        Extract structured product data from a product page using OpenAI
        
        Args:
            page_content: The markdown/text content of the page
            page_url: The URL of the page
            
        Returns:
            Dictionary with product data in Shopify format, or None if extraction fails
        """
        try:
            logger.info(f"🤖 Extracting product data from: {page_url}")
            
            # Truncate very long content to save tokens (keep first 8000 chars)
            truncated_content = page_content[:8000]
            
            prompt = f"""Your task: EXACTLY REPLICATE the product data from this e-commerce page. DO NOT create, infer, or modify anything.

URL: {page_url}

Content:
{truncated_content}

Return a JSON object with this structure:
{{
  "title": "EXACT product name from the page (copy verbatim)",
  "body_html": "<p>FULL detailed product description with ALL content from the page</p><table><tr><th>Specification</th><th>Value</th></tr><tr><td>Material</td><td>Steel</td></tr></table><ul><li>Feature 1</li><li>Feature 2</li></ul>",
  "vendor": "Brand/manufacturer name from page",
  "product_type": "Category from page",
  "tags": ["tag1", "tag2"],
  "variants": [
    {{
      "title": "Variant option text (e.g., '1ft', 'Red', 'Small')",
      "price": "29.99",
      "compare_at_price": "39.99",
      "sku": "SKU-123",
      "option1": "1ft",
      "option2": null,
      "option3": null
    }}
  ],
  "images": [
    {{
      "src": "https://example.com/image1.jpg",
      "position": 1
    }}
  ],
  "options": [
    {{
      "name": "Length",
      "values": ["1ft", "2ft", "3ft", "4ft", "5ft", "6ft"]
    }}
  ]
}}

🚨 CRITICAL RULES - EXACT REPLICATION ONLY:

1. **EXTRACT FULL DETAILED DESCRIPTION WITH HTML TABLES**:
   - Extract the COMPLETE product description - DO NOT summarize or shorten
   - Look for specification tables, feature tables, size charts, dimension tables
   - Convert tables to proper HTML <table> format with <tr>, <th>, <td> tags
   - Common table patterns in markdown:
     * "| Specification | Value |" → Convert to <table><tr><th>Specification</th><th>Value</th></tr>...
     * "Material: Steel, Weight: 5kg" → Convert to table rows
     * Any structured data with labels and values
   - Preserve all formatting: <p> for paragraphs, <ul>/<li> for lists, <table> for tables
   - Include ALL content sections: description, features, specifications, dimensions, materials, usage instructions
   - If the page has multiple description sections, include ALL of them
   - Use proper HTML tags for structure and readability

2. **REPLICATE EVERY VARIANT EXACTLY AS IT APPEARS**:
   - **CRITICAL: Check for JSON-LD structured data FIRST** (most reliable source):
     * Look for <script type="application/ld+json"> tags
     * Extract variant data from Schema.org Product markup
     * Common pattern: "offers": [{{"sku": "ABC-2", "price": "114.00"}}, {{"sku": "ABC-3", "price": "138.00"}}...]
     * SKUs often encode variant info: "TRP608-2" = 2ft, "TRP608-3" = 3ft, etc.
     * Extract ALL offers/variants from the JSON-LD data with their exact prices

   - Also look for variant selectors in HTML: <select>, <option>, radio buttons, data attributes
   - Common HTML patterns:
     * <select name="size"><option>1ft</option><option>2ft</option>... → Extract ALL options
     * <input type="radio" value="Small"> → Extract ALL radio values
     * data-variant="Red" or data-size="Large" → Extract from data attributes
     * JavaScript variant arrays: variants: [{{"title": "1ft"}}, {{"title": "2ft"}}...] → Extract ALL

   - If the page shows a dropdown with "1ft, 2ft, 3ft, 4ft, 5ft, 6ft" → Create 6 separate variant entries
   - If the page shows "Small, Medium, Large" → Create 3 variant entries
   - DO NOT skip, combine, or summarize variants
   - DO NOT create variants that don't exist on the page
   - Copy the EXACT text from each option (including units, capitalization, spacing)

3. **USE THE EXACT OPTION NAME FROM THE PAGE**:
   - If the page says "Select Length:" → Use "Length" as the option name
   - If the page says "Choose Size:" → Use "Size" as the option name
   - If the page says "Colour:" → Use "Colour" (their spelling)
   - DO NOT use generic names like "Option", "Option 1", "Title"
   - DO NOT infer or create option names - copy them from the page labels

4. **EXACT OPTION VALUES**:
   - Copy option values character-for-character from the page
   - If page shows "1ft" → use "1ft" (not "1 ft" or "12 inches")
   - If page shows "Small (S)" → use "Small (S)" (not just "Small")
   - Preserve all formatting, units, and punctuation

5. **EXTRACT ACTUAL PRICES FOR EACH VARIANT** - CRITICAL FOR SUCCESS:

   **PRIORITY 1: JSON-LD structured data in <script type="application/ld+json">**:
   ```json
   Example to look for:
   {
     "@type": "Product",
     "offers": [
       {"sku": "TRP608-2", "price": "114.00"},
       {"sku": "TRP608-3", "price": "138.00"},
       {"sku": "TRP608-4", "price": "162.00"}
     ]
   }
   ```
   - Extract price for EACH offer/SKU
   - Match SKU to variant (e.g., "TRP608-2" = 2ft variant → price: "114.00")
   - This is the MOST RELIABLE source for accurate prices

   **PRIORITY 2: JavaScript product data**:
   - Look for: `var product = {`, `window.productData =`, `data-product-json=`
   - Pattern: `variants: [{"id": 123, "title": "2ft", "price": 5500}]` (price in cents)
   - Convert cents to decimal: 5500 → "55.00"

   **PRIORITY 3: HTML visible prices**:
   - Pattern 1: "£114.00" next to "2ft" option in dropdown
   - Pattern 2: Price table showing "2ft: £114.00 | 3ft: £138.00"
   - Pattern 3: Data attributes: `data-variant-price="114.00"`
   - Pattern 4: "From £114.00" means base price (use for all if no variant prices found)

   **CRITICAL RULES**:
   - Each variant MUST have a price > 0
   - If you find prices for variants, assign them correctly
   - If all variants share one price, use that for all
   - DO NOT leave prices as 0.00, null, or empty
   - If absolutely no price found, skip the product entirely
   - Remove currency symbols (£, $, €) but keep the number

6. **FAITHFUL IMAGE EXTRACTION**:
   - Extract ONLY images that appear in the page content
   - Look for: ![alt](URL), <img src="URL">, or direct image URLs
   - Include ALL product images in the order they appear
   - Use complete URLs including https://

7. **NO CREATION OR INFERENCE**:
   - DO NOT add tags not mentioned on the page
   - DO NOT create descriptions if missing
   - DO NOT infer vendor names
   - Only extract what explicitly exists on the page

8. **Single-variant products**:
   - If NO selectors/dropdowns exist → option1="Default", options=[{{"name": "Title", "values": ["Default Title"]}}]
   - Do NOT create fake variants for single-variant products

9. Return ONLY valid JSON, no additional text

EXTRACT THE PRODUCT DATA EXACTLY AS IT APPEARS:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product data extraction expert. Extract structured product information and return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=4096,  # Increased to accommodate detailed descriptions with HTML tables
                response_format={"type": "json_object"}
            )
            
            json_str = response.choices[0].message.content.strip()
            product_data = json.loads(json_str)
            
            # Add source URL for reference
            product_data['source_url'] = page_url
            
            # Filter out SVG and unsupported image formats
            if 'images' in product_data and product_data['images']:
                valid_images = []
                for img in product_data['images']:
                    img_url = img.get('src', '') if isinstance(img, dict) else img
                    # Skip SVG, WebP, ICO, and GIF files
                    if not img_url.lower().endswith(('.svg', '.webp', '.ico', '.gif')):
                        valid_images.append(img)
                    else:
                        logger.info(f"⚠️ Filtered out unsupported image format: {img_url}")
                product_data['images'] = valid_images
            
            # Validate required fields
            title = product_data.get('title', '').strip()
            if not title:
                logger.warning(f"⚠️  No title extracted from {page_url}")
                return None
            
            # Filter out invalid titles (cart messages, navigation, etc.)
            invalid_titles = [
                'item added to your cart',
                'added to cart',
                'cart',
                'checkout',
                'shopping cart',
                'your cart',
                'view cart',
                'continue shopping',
                'home',
                'shop',
                'products',
                'categories'
            ]
            
            if title.lower() in invalid_titles:
                logger.warning(f"⚠️  Invalid title detected (cart/navigation element): '{title}' - skipping")
                return None
            
            if not product_data.get('variants') or len(product_data['variants']) == 0:
                logger.warning(f"⚠️  No variants extracted, creating default variant")
                product_data['variants'] = [{
                    "title": "Default",
                    "price": "0.00",
                    "sku": "",
                    "option1": "Default",
                    "option2": None,
                    "option3": None
                }]
            
            logger.info(f"✅ Extracted product: {product_data['title']} ({len(product_data['variants'])} variants)")

            return product_data

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from OpenAI response: {str(e)}")
            logger.error(f"❌ Response preview (first 500 chars): {json_str[:500] if 'json_str' in locals() else 'N/A'}")
            logger.error(f"❌ Response preview (last 200 chars): {json_str[-200:] if 'json_str' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting product data: {str(e)}")
            return None

    def extract_products_from_pages_simple(self, pages: List[Dict]) -> List[Dict]:
        """
        Simple extraction - just get basic product data from each page
        Grouping will be done by ProductGrouper afterwards
        
        Args:
            pages: List of page dictionaries from Firecrawl
            
        Returns:
            List of extracted product data dictionaries (ungrouped)
        """
        products = []
        
        logger.info(f"🔍 Extracting product data from {len(pages)} pages (simple mode)...")
        
        for i, page in enumerate(pages, 1):
            page_url = page.get('url', '')
            # Use HTML first (preserves variant selectors better), fallback to markdown
            page_content = page.get('html', '') or page.get('markdown', '')

            if not page_content:
                logger.warning(f"⏭️  Skipping page {i}/{len(pages)}: No content")
                continue
            
            logger.info(f"📄 Processing page {i}/{len(pages)}: {page_url}")
            
            # Check if it's a product page
            if not self.is_product_page(page_content, page_url):
                logger.info(f"⏭️  Not a product page, skipping")
                continue
            
            # Extract product data (no merging, just extraction)
            product_data = self.extract_product_data(page_content, page_url)
            
            if product_data:
                # Add markdown for grouper
                product_data['markdown'] = page_content
                product_data['url'] = page_url
                products.append(product_data)
                logger.info(f"✅ Product extracted: {product_data['title']}")
            else:
                logger.warning(f"⚠️  Failed to extract product data from {page_url}")
        
        logger.info(f"🎉 Extracted {len(products)} products from {len(pages)} pages")
        
        return products
    
    def extract_products_from_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Process multiple pages and extract product data from product pages only
        
        Args:
            pages: List of page dictionaries from Firecrawl
            
        Returns:
            List of extracted product data dictionaries
        """
        products = []
        
        logger.info(f"🔍 Processing {len(pages)} pages to find products...")
        
        # First pass: identify all product pages and their URLs
        product_pages = []
        
        for i, page in enumerate(pages, 1):
            page_url = page.get('url', '')
            # Use HTML first (preserves variant selectors better), fallback to markdown
            page_content = page.get('html', '') or page.get('markdown', '')

            if not page_content:
                logger.warning(f"⏭️  Skipping page {i}/{len(pages)}: No content")
                continue
            
            logger.info(f"📄 Processing page {i}/{len(pages)}: {page_url}")
            
            # Check if it's a product page
            if not self.is_product_page(page_content, page_url):
                logger.info(f"⏭️  Not a product page, skipping")
                continue
            
            # Store page info for processing
            product_pages.append({
                'page': page,
                'url': page_url,
                'content': page_content,
                'url_depth': page_url.count('/')  # Shorter URLs are usually parent pages
            })
        
        # Sort by URL depth (parent pages first)
        product_pages.sort(key=lambda x: x['url_depth'])
        
        logger.info(f"📊 Found {len(product_pages)} product pages, processing in order (parents first)...")
        
        # Second pass: extract products in order
        for i, page_info in enumerate(product_pages, 1):
            page_url = page_info['url']
            page_content = page_info['content']
            
            # Extract product data
            product_data = self.extract_product_data(page_content, page_url)
            
            if product_data:
                # Add metadata
                product_data['_url_depth'] = page_info['url_depth']
                product_data['_source_url'] = page_url
                products.append(product_data)
                logger.info(f"✅ Product extracted: {product_data['title']} (depth: {page_info['url_depth']})")
            else:
                logger.warning(f"⚠️  Failed to extract product data from {page_url}")
        
        logger.info(f"🎉 Extracted {len(products)} products from {len(product_pages)} pages")
        
        # Merge products with the same title (variants from different pages)
        # Parent products (lower depth) will be processed first
        merged_products = self._merge_product_variants(products)
        
        if len(merged_products) < len(products):
            logger.info(f"🔄 Merged {len(products)} products into {len(merged_products)} products with variants")
        
        return merged_products
    
    def _merge_product_variants(self, products: List[Dict]) -> List[Dict]:
        """
        Merge products that are likely variants of each other based on similarity
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of merged product dictionaries
        """
        if not products:
            return []
        
        merged = []
        
        for product in products:
            title = product.get('title', '').strip()
            
            if not title:
                continue
            
            # Find if this product is similar to any existing merged product
            matched = False
            
            for existing in merged:
                if self._are_products_similar(product, existing):
                    # Merge this product as a variant of the existing one
                    self._merge_into_existing(product, existing)
                    matched = True
                    break
            
            if not matched:
                # This is a new unique product
                merged.append(product)
        
        return merged
    
    def _are_products_similar(self, product1: Dict, product2: Dict) -> bool:
        """
        Check if two products are likely variants of the same base product
        
        Args:
            product1: First product dictionary
            product2: Second product dictionary
            
        Returns:
            True if products are similar enough to be variants
        """
        title1 = product1.get('title', '').lower()
        title2 = product2.get('title', '').lower()
        
        # Remove dimensions in parentheses for comparison
        import re
        clean_title1 = re.sub(r'\s*\([^)]*\)\s*', ' ', title1).strip()
        clean_title2 = re.sub(r'\s*\([^)]*\)\s*', ' ', title2).strip()
        
        # Calculate word overlap
        words1 = set(clean_title1.split())
        words2 = set(clean_title2.split())
        
        # Remove common words that don't matter
        common_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'of', 'in', 'on', 'at'}
        words1 = words1 - common_words
        words2 = words2 - common_words
        
        if not words1 or not words2:
            return False
        
        # Calculate similarity (Jaccard similarity)
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        similarity = intersection / union if union > 0 else 0
        
        # If 70%+ words match, they're likely the same product
        return similarity >= 0.7
    
    def _merge_into_existing(self, new_product: Dict, existing: Dict):
        """
        Merge a new product into an existing product as a variant
        
        Args:
            new_product: Product to merge
            existing: Existing product to merge into
        """
        existing_title = existing.get('title', '')
        new_title = new_product.get('title', '')
        existing_depth = existing.get('_url_depth', 999)
        new_depth = new_product.get('_url_depth', 999)
        
        logger.info(f"🔄 Merging '{new_title}' (depth {new_depth}) into '{existing_title}' (depth {existing_depth})")
        
        # Keep the title from the parent page (lower depth = parent)
        # If depths are equal, keep the longer, more descriptive title
        import re
        
        if new_depth < existing_depth:
            # New product is the parent, use its title
            base_title = re.sub(r'\s*\([^)]*\)\s*', '', new_title).strip()
            logger.info(f"📌 Using new product as parent: '{base_title}'")
        elif existing_depth < new_depth:
            # Existing is the parent, keep its title
            base_title = re.sub(r'\s*\([^)]*\)\s*', '', existing_title).strip()
            logger.info(f"📌 Keeping existing as parent: '{base_title}'")
        else:
            # Same depth, use longer title (more descriptive)
            clean_existing = re.sub(r'\s*\([^)]*\)\s*', '', existing_title).strip()
            clean_new = re.sub(r'\s*\([^)]*\)\s*', '', new_title).strip()
            base_title = clean_existing if len(clean_existing) >= len(clean_new) else clean_new
            logger.info(f"📌 Using longer title as parent: '{base_title}'")
        
        existing['title'] = base_title
        
        # Merge variants
        new_variants = new_product.get('variants', [])
        existing_variants = existing.get('variants', [])
        
        for new_variant in new_variants:
            # Update variant title to include the full product name for distinction
            new_variant['title'] = new_title
            # Update option1 to be the variant-specific part (dimensions)
            dimensions = re.search(r'\(([^)]+)\)', new_title)
            if dimensions:
                new_variant['option1'] = dimensions.group(1)
            else:
                new_variant['option1'] = new_title
            existing_variants.append(new_variant)
        
        existing['variants'] = existing_variants
        
        # Merge images (avoid duplicates)
        new_images = new_product.get('images', [])
        existing_images = existing.get('images', [])
        existing_image_urls = {img.get('src') for img in existing_images}
        
        for new_image in new_images:
            if new_image.get('src') not in existing_image_urls:
                existing_images.append(new_image)
        
        existing['images'] = existing_images
        
        # Update options to use dimensions as option values
        option_values = []
        for v in existing_variants:
            opt = v.get('option1', 'Default')
            if opt not in option_values:
                option_values.append(opt)
        
        existing['options'] = [
            {
                "name": "Size",
                "values": option_values
            }
        ]
        
        logger.info(f"✅ Merged successfully: '{clean_title}' (now has {len(existing_variants)} variants)")
