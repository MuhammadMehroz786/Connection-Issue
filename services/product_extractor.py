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
            
            prompt = f"""Extract product information from this e-commerce page and format it for Shopify.

URL: {page_url}

Content:
{truncated_content}

Extract and return a JSON object with this EXACT structure:
{{
  "title": "Exact product name from the page",
  "body_html": "Full product description in HTML format",
  "vendor": "Brand or manufacturer name",
  "product_type": "Category or type",
  "tags": ["tag1", "tag2", "tag3"],
  "variants": [
    {{
      "title": "Variant name (use the full product name if only one variant)",
      "price": "29.99",
      "compare_at_price": "39.99",
      "sku": "SKU-123",
      "option1": "Default",
      "option2": null,
      "option3": null,
      "inventory_quantity": 10
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
      "name": "Option",
      "values": ["Default"]
    }}
  ]
}}

IMPORTANT RULES:
1. Extract the EXACT product title as shown on the page - do NOT modify it
2. Extract ALL variants if multiple sizes/colors/options exist on the page
3. **CRITICAL FOR VARIANTS - EACH VARIANT NEEDS ITS OWN PRICE**:
   - CAREFULLY search the page content for variant-specific pricing
   - Look for price tables, dropdown options with prices, or variant listings
   - Common patterns: "Size S: £25", "Small - £25.00", "Option 1 (£30)", "1m x 2m: £45.99"
   - Check for JavaScript data, JSON objects, or structured data with variant prices
   - If you find a price selector or variant dropdown, extract the price for EACH option
   - **DO NOT assume all variants have the same price** - look carefully for individual prices
   - Only use the same price for all variants if you're absolutely certain they cost the same
   - If variant prices are not clearly shown, look for patterns like "from £X" which indicates varying prices
4. If only one variant exists, use "Default" for option1
5. Use actual prices found on the page (remove currency symbols like £, $, €)
6. **CRITICAL**: Extract ALL product image URLs from the markdown content
   - Look for markdown images: ![alt](https://example.com/image.jpg)
   - Look for HTML images: <img src="https://example.com/image.jpg">
   - Look for direct URLs in the content
   - Extract the FULL URL including https://
   - Do NOT use placeholder URLs
6. Create meaningful tags from the product category, features, and attributes
7. Format body_html with proper HTML tags (<p>, <ul>, <li>, etc.)
8. If information is missing, use null or empty array []
9. Return ONLY valid JSON, no additional text

Extract the product data now:"""

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
                max_tokens=2000,
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
            page_content = page.get('markdown', '') or page.get('html', '')
            
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
            page_content = page.get('markdown', '') or page.get('html', '')
            
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
