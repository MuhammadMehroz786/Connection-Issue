"""
Test script to verify variant extraction from HTML content
"""
import os
from dotenv import load_dotenv
from services.product_extractor import ProductExtractorService

load_dotenv()

# Sample HTML with variants (simulating a product page with size dropdown)
sample_html = """
<html>
<head><title>Galvanised Steel Post</title></head>
<body>
<h1>Galvanised Steel Post - Security Bollard</h1>

<div class="product-description">
    <p>High-quality galvanised steel security post, perfect for preventing vehicle access.</p>
    <p>Weather resistant and durable construction.</p>
</div>

<div class="product-specs">
    <h2>Specifications</h2>
    <table>
        <tr><th>Material</th><td>Galvanised Steel</td></tr>
        <tr><th>Diameter</th><td>76mm</td></tr>
        <tr><th>Installation</th><td>Bolt Down</td></tr>
    </table>
</div>

<div class="product-options">
    <label for="size">Select Length:</label>
    <select id="size" name="size">
        <option value="1ft" data-price="45.00">1ft - £45.00</option>
        <option value="2ft" data-price="55.00">2ft - £55.00</option>
        <option value="3ft" data-price="65.00">3ft - £65.00</option>
        <option value="4ft" data-price="75.00">4ft - £75.00</option>
        <option value="5ft" data-price="85.00">5ft - £85.00</option>
        <option value="6ft" data-price="95.00">6ft - £95.00</option>
    </select>
</div>

<div class="price">
    <span class="current-price">From £45.00</span>
</div>

<div class="product-images">
    <img src="https://example.com/post-image-1.jpg" alt="Steel Post Front View">
    <img src="https://example.com/post-image-2.jpg" alt="Steel Post Side View">
</div>

<button class="add-to-cart">Add to Cart</button>

<div class="features">
    <h3>Features:</h3>
    <ul>
        <li>Hot-dip galvanised finish</li>
        <li>Corrosion resistant</li>
        <li>Easy bolt-down installation</li>
        <li>Professional grade quality</li>
    </ul>
</div>
</body>
</html>
"""

def test_variant_extraction():
    """Test that all 6 variants are extracted from HTML"""
    print("🧪 Testing Variant Extraction with HTML Content\n")
    print("=" * 70)

    # Initialize extractor
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return

    extractor = ProductExtractorService(api_key)

    # Test extraction
    print("\n📄 Testing with sample HTML containing 6 size variants (1ft-6ft)...")
    print("   Expected: 6 variants extracted")
    print("   Expected option name: 'Length' (from 'Select Length:' label)\n")

    product_data = extractor.extract_product_data(
        page_content=sample_html,
        page_url="https://example.com/test-product"
    )

    if not product_data:
        print("❌ FAILED: No product data extracted")
        return

    print(f"✅ Product extracted: {product_data.get('title')}")
    print(f"\n📊 Variants found: {len(product_data.get('variants', []))}")

    variants = product_data.get('variants', [])
    if len(variants) < 6:
        print(f"⚠️  WARNING: Only {len(variants)} variants extracted (expected 6)")
    else:
        print(f"✅ SUCCESS: All {len(variants)} variants extracted!")

    print("\n" + "=" * 70)
    print("Variant Details:")
    print("=" * 70)

    for idx, variant in enumerate(variants, 1):
        print(f"\nVariant {idx}:")
        print(f"  Title: {variant.get('title')}")
        print(f"  Price: £{variant.get('price')}")
        print(f"  Option1: {variant.get('option1')}")
        print(f"  Option2: {variant.get('option2')}")
        print(f"  Option3: {variant.get('option3')}")

    # Check options
    print("\n" + "=" * 70)
    print("Options Configuration:")
    print("=" * 70)

    options = product_data.get('options', [])
    for idx, opt in enumerate(options, 1):
        print(f"\nOption {idx}:")
        print(f"  Name: {opt.get('name')}")
        print(f"  Values: {opt.get('values')}")

    # Check if option name is meaningful
    if options:
        option_name = options[0].get('name', '')
        if option_name in ['Option', 'Option 1', 'Title', 'Default']:
            print(f"\n⚠️  WARNING: Generic option name detected: '{option_name}'")
            print("   Expected: 'Length' (from HTML label)")
        else:
            print(f"\n✅ SUCCESS: Meaningful option name: '{option_name}'")

    # Check description
    print("\n" + "=" * 70)
    print("Description (HTML):")
    print("=" * 70)
    print(product_data.get('body_html', 'N/A')[:500])
    if '<table>' in product_data.get('body_html', ''):
        print("\n✅ SUCCESS: HTML table found in description!")
    else:
        print("\n⚠️  WARNING: No HTML table found in description")

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_variant_extraction()
