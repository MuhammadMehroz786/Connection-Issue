"""
Product Variant Grouper
Groups e-commerce products with their variants using URL, SKU, and title analysis
"""

import re
import logging
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs
from difflib import SequenceMatcher
from collections import defaultdict

logger = logging.getLogger(__name__)


class ProductVariantGrouper:
    """
    Groups e-commerce products and their variants by analyzing multiple signals:
    - URL patterns and product IDs
    - SKU patterns
    - Title normalization and similarity
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize the grouper
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider products as variants
        """
        self.similarity_threshold = similarity_threshold
        
        # Common variant keywords to remove from titles
        self.variant_keywords = {
            # Sizes
            'xs', 'small', 'medium', 'large', 'xl', 'xxl', 'xxxl',
            's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl',
            # Colors
            'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple',
            'pink', 'brown', 'grey', 'gray', 'navy', 'beige', 'silver', 'gold',
            # Descriptors
            'extra wide', 'extra-wide', 'wide', 'narrow', 'standard', 'heavy duty',
            'lightweight', 'professional', 'commercial', 'industrial', 'portable'
        }
        
        # Common words to ignore in comparison
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'of', 'in', 'on', 'at'}
    
    def parse_markdown(self, markdown_content: str) -> Dict:
        """
        Extract product information from markdown content
        
        Args:
            markdown_content: Raw markdown text
            
        Returns:
            Dictionary with extracted fields (title, sku, price, etc.)
        """
        if not markdown_content:
            return {}
        
        extracted = {}
        
        # Extract title (first heading)
        title_match = re.search(r'^#+ (.+)$', markdown_content, re.MULTILINE)
        if title_match:
            extracted['title'] = title_match.group(1).strip()
        
        # Extract SKU
        sku_match = re.search(r'SKU:?\s*([A-Z0-9\-_]+)', markdown_content, re.IGNORECASE)
        if sku_match:
            extracted['sku'] = sku_match.group(1).strip()
        
        # Extract Product ID
        id_match = re.search(r'Product\s+ID:?\s*([A-Z0-9\-_]+)', markdown_content, re.IGNORECASE)
        if id_match:
            extracted['product_id'] = id_match.group(1).strip()
        
        # Extract Price
        price_match = re.search(r'Price:?\s*[£$€]?\s*([0-9,]+\.?[0-9]*)', markdown_content, re.IGNORECASE)
        if price_match:
            extracted['price'] = price_match.group(1).replace(',', '')
        
        # Extract Color
        color_match = re.search(r'Colou?r:?\s*([A-Za-z\s]+)', markdown_content, re.IGNORECASE)
        if color_match:
            extracted['color'] = color_match.group(1).strip()
        
        # Extract Size
        size_match = re.search(r'Size:?\s*([A-Za-z0-9\s\-x×]+)', markdown_content, re.IGNORECASE)
        if size_match:
            extracted['size'] = size_match.group(1).strip()
        
        return extracted
    
    def extract_url_signals(self, url: str) -> Dict:
        """
        Extract product identifiers from URL
        
        Args:
            url: Product URL
            
        Returns:
            Dictionary with URL-based signals
        """
        if not url:
            return {}
        
        parsed = urlparse(url)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        signals = {
            'url': url,
            'path': path,
            'query_params': query
        }
        
        # Extract product ID from common URL patterns
        # Pattern 1: /products/123 or /product/123 or /p/123
        id_match = re.search(r'/(?:products?|p|item)s?/([a-z0-9\-]+)', path, re.IGNORECASE)
        if id_match:
            signals['url_product_id'] = id_match.group(1)
        
        # Pattern 2: /product-name-123
        trailing_id = re.search(r'-(\d+)/?$', path)
        if trailing_id:
            signals['trailing_id'] = trailing_id.group(1)
        
        # Extract base path (without variant parameters)
        # Remove trailing numbers, colors, sizes
        base_path = re.sub(r'[-_](xs|small|medium|large|xl|xxl|\d+x\d+|black|white|red|blue)/?$', '', path, flags=re.IGNORECASE)
        signals['base_path'] = base_path
        
        # Check for variant query parameters
        variant_params = {}
        for key in ['color', 'colour', 'size', 'variant', 'option', 'style']:
            if key in query:
                variant_params[key] = query[key][0]
        
        if variant_params:
            signals['variant_params'] = variant_params
        
        return signals
    
    def extract_sku_base(self, sku: str) -> Optional[str]:
        """
        Extract base SKU by removing variant suffixes
        
        Args:
            sku: Full SKU (e.g., "PROD-001-RED-L")
            
        Returns:
            Base SKU (e.g., "PROD-001")
        """
        if not sku:
            return None
        
        # Common SKU patterns:
        # PROD-001-RED-L → PROD-001
        # TSH001REDL → TSH001
        # ITEM_123_BLU_M → ITEM_123
        
        # Try hyphen-separated
        parts = sku.split('-')
        if len(parts) >= 2:
            # Keep first 1-2 parts (usually base SKU)
            return '-'.join(parts[:2])
        
        # Try underscore-separated
        parts = sku.split('_')
        if len(parts) >= 2:
            return '_'.join(parts[:2])
        
        # Try to remove trailing variant codes (last 1-3 chars if letters)
        if len(sku) > 4:
            # Remove trailing size/color codes like "REDL", "BLUM", "XL"
            base = re.sub(r'[A-Z]{1,4}$', '', sku)
            if base and base != sku:
                return base
        
        # Return as-is if no pattern found
        return sku
    
    def normalize_title(self, title: str) -> str:
        """
        Normalize product title by removing variant information
        
        Args:
            title: Original product title
            
        Returns:
            Normalized title
        """
        if not title:
            return ""
        
        normalized = title.lower().strip()
        
        # Remove dimensions in parentheses (e.g., "(2000x300x500kg)")
        normalized = re.sub(r'\s*\([^)]*\)\s*', ' ', normalized)
        
        # Remove variant keywords
        for keyword in self.variant_keywords:
            # Remove as whole word
            normalized = re.sub(r'\b' + re.escape(keyword) + r'\b', '', normalized, flags=re.IGNORECASE)
        
        # Remove size patterns (e.g., "32oz", "5kg", "2000x300")
        normalized = re.sub(r'\b\d+\s*(oz|kg|g|lb|mm|cm|m|inch|in|ft)\b', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\b\d+x\d+(?:x\d+)?\b', '', normalized, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        if not str1 or not str2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _is_variant(self, product1: Dict, product2: Dict) -> Tuple[bool, str]:
        """
        Determine if two products are variants of each other
        
        Args:
            product1: First product dictionary
            product2: Second product dictionary
            
        Returns:
            Tuple of (is_variant: bool, reason: str)
        """
        # Signal 1: URL-based matching
        url1_signals = product1.get('_url_signals', {})
        url2_signals = product2.get('_url_signals', {})
        
        # Check if they share the same base path
        if url1_signals.get('base_path') and url2_signals.get('base_path'):
            if url1_signals['base_path'] == url2_signals['base_path']:
                return True, "same_base_path"
        
        # Check if they share the same product ID in URL
        if url1_signals.get('url_product_id') and url2_signals.get('url_product_id'):
            if url1_signals['url_product_id'] == url2_signals['url_product_id']:
                return True, "same_url_product_id"
        
        # Signal 2: SKU-based matching
        sku1_base = product1.get('_sku_base')
        sku2_base = product2.get('_sku_base')
        
        if sku1_base and sku2_base and sku1_base == sku2_base:
            return True, "same_sku_base"
        
        # Signal 3: Title similarity (normalized)
        title1_norm = product1.get('_normalized_title', '')
        title2_norm = product2.get('_normalized_title', '')
        
        if title1_norm and title2_norm:
            # Calculate word overlap (Jaccard similarity)
            words1 = set(title1_norm.split()) - self.stop_words
            words2 = set(title2_norm.split()) - self.stop_words
            
            if words1 and words2:
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                jaccard = intersection / union if union > 0 else 0
                
                if jaccard >= self.similarity_threshold:
                    return True, f"title_similarity_{jaccard:.2f}"
        
        return False, "no_match"
    
    def group_products(self, products: List[Dict]) -> List[Dict]:
        """
        Group products with their variants (optimized for large datasets)
        
        Args:
            products: List of product dictionaries with 'url' and 'markdown' or extracted fields
            
        Returns:
            List of grouped products with variants
        """
        logger.info(f"🔍 Grouping {len(products)} products...")
        
        # Step 1: Enrich products with signals
        enriched_products = []
        
        for idx, product in enumerate(products):
            if idx % 100 == 0:
                logger.info(f"📊 Enriching products: {idx}/{len(products)}")
            
            # Parse markdown if present (but don't overwrite existing extracted fields)
            if 'markdown' in product or 'markdown_content' in product:
                markdown = product.get('markdown') or product.get('markdown_content', '')
                parsed = self.parse_markdown(markdown)
                # Only update fields that don't already exist (don't overwrite OpenAI-extracted data)
                for key, value in parsed.items():
                    if key not in product or not product[key]:
                        product[key] = value
            
            # Extract URL signals
            url = product.get('url', '')
            product['_url_signals'] = self.extract_url_signals(url)
            
            # Extract SKU base
            sku = product.get('sku', '')
            product['_sku_base'] = self.extract_sku_base(sku)
            
            # Normalize title
            title = product.get('title', '')
            product['_normalized_title'] = self.normalize_title(title)
            
            enriched_products.append(product)
        
        logger.info(f"✅ Enriched {len(enriched_products)} products with signals")
        
        # Step 2: Build indexes for fast lookup (avoid O(n²))
        logger.info(f"🔍 Building indexes for fast grouping...")
        
        # Index by base_path
        path_index = defaultdict(list)
        # Index by SKU base
        sku_index = defaultdict(list)
        # Index by normalized title
        title_index = defaultdict(list)
        
        for i, product in enumerate(enriched_products):
            base_path = product.get('_url_signals', {}).get('base_path', '')
            if base_path:
                path_index[base_path].append(i)
            
            sku_base = product.get('_sku_base', '')
            if sku_base:
                sku_index[sku_base].append(i)
            
            norm_title = product.get('_normalized_title', '')
            if norm_title:
                # Index by first 3 words for faster lookup
                words = norm_title.split()[:3]
                key = ' '.join(words) if words else norm_title
                title_index[key].append(i)
        
        logger.info(f"✅ Built indexes: {len(path_index)} paths, {len(sku_index)} SKUs, {len(title_index)} titles")
        
        # Step 3: Group products using indexes
        groups = []
        processed = set()
        
        for i, product in enumerate(enriched_products):
            if i in processed:
                continue
            
            if i % 50 == 0:
                logger.info(f"📊 Grouping progress: {i}/{len(enriched_products)} ({len(groups)} groups so far)")
            
            # Start a new group with this product as parent
            group = {
                'parent_product': {
                    'title': product.get('title', ''),
                    'url': product.get('url', ''),
                    'sku': product.get('sku', ''),
                    'price': product.get('price', ''),
                    'product_data': product
                },
                'variants': [],
                'total_variants': 1,
                'group_identifiers': {
                    'base_title': product.get('_normalized_title', ''),
                    'url_base': product.get('_url_signals', {}).get('base_path', ''),
                    'sku_base': product.get('_sku_base', '')
                }
            }
            
            processed.add(i)
            
            # Find potential variants using indexes (much faster than O(n²))
            candidates = set()
            
            # Add candidates from path index
            base_path = product.get('_url_signals', {}).get('base_path', '')
            if base_path and base_path in path_index:
                candidates.update(path_index[base_path])
            
            # Add candidates from SKU index
            sku_base = product.get('_sku_base', '')
            if sku_base and sku_base in sku_index:
                candidates.update(sku_index[sku_base])
            
            # Add candidates from title index
            norm_title = product.get('_normalized_title', '')
            if norm_title:
                words = norm_title.split()[:3]
                key = ' '.join(words) if words else norm_title
                if key in title_index:
                    candidates.update(title_index[key])
            
            # Check only candidates (not all products)
            for j in candidates:
                if j in processed or j == i:
                    continue
                
                other_product = enriched_products[j]
                is_variant, reason = self._is_variant(product, other_product)
                
                if is_variant:
                    group['variants'].append({
                        'title': other_product.get('title', ''),
                        'url': other_product.get('url', ''),
                        'sku': other_product.get('sku', ''),
                        'price': other_product.get('price', ''),
                        'product_data': other_product,
                        'match_reason': reason
                    })
                    group['total_variants'] += 1
                    processed.add(j)
            
            if group['total_variants'] > 1:
                logger.info(f"🔗 Grouped '{product.get('title', '')}' with {group['total_variants'] - 1} variants")
            
            groups.append(group)
        
        logger.info(f"🎉 Grouped {len(products)} products into {len(groups)} unique products")
        logger.info(f"📊 Average variants per product: {len(products) / len(groups):.1f}")
        
        # Log grouping statistics
        variant_counts = [g['total_variants'] for g in groups]
        max_variants = max(variant_counts) if variant_counts else 0
        logger.info(f"📊 Max variants in a single product: {max_variants}")
        
        return groups
