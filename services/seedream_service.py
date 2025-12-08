"""
SeeDream Service (doubao-seedream-4-5-251128)
Handles image generation using SeeDream API for both Image 1 and Image 2
"""

import requests
import base64
import logging
import io
from PIL import Image
from typing import Optional, List

logger = logging.getLogger(__name__)


class SeeDreamService:
    """Service for generating images using SeeDream API (doubao-seedream-4-5-251128)"""

    def __init__(self, api_key):
        """
        Initialize SeeDream service
        
        Args:
            api_key: SeeDream API key
        """
        self.api_key = api_key
        self.base_url = "https://api.cometapi.com/v1/images/generations"
        self.model = "doubao-seedream-4-5-251128"
        
        if not self.api_key:
            logger.warning("⚠️ No SeeDream API key provided")
        else:
            logger.info("✅ SeeDream service initialized")

    def _download_and_encode_images(self, image_urls: List[str]) -> List[str]:
        """
        Download and encode images to base64
        
        Args:
            image_urls: List of image URLs to download and encode
            
        Returns:
            List of base64 encoded images with data URL prefix
        """
        encoded_images = []
        
        for idx, image_url in enumerate(image_urls, 1):
            try:
                # Handle data URLs (already base64)
                if image_url.startswith('data:image'):
                    logger.info(f"   Image {idx}: Already base64 encoded")
                    encoded_images.append(image_url)
                    continue
                
                logger.info(f"📥 Downloading reference image {idx}/{len(image_urls)}")
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()

                # Load image and convert to RGB
                img = Image.open(io.BytesIO(img_response.content))
                if img.mode not in ('RGB', 'L'):
                    logger.info(f"📸 Converting image {idx} from {img.mode} mode to RGB")
                    img = img.convert('RGB')

                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=95)
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                encoded_images.append(f"data:image/jpeg;base64,{img_base64}")
                logger.info(f"✅ Reference image {idx} encoded ({len(img_base64)} chars)")
                
            except Exception as e:
                logger.error(f"❌ Failed to encode image {idx}: {str(e)}, SVG file type is not a product image.")
                continue
        
        logger.info(f"✅ Total reference images encoded: {len(encoded_images)}")
        return encoded_images

    def edit_product_image(self, original_image_url: str, product_title: str, variation="product_in_use", all_image_urls=None):
        """
        Edit product image using SeeDream API
        
        Args:
            original_image_url: URL of the original product image
            product_title: Product title for context
            variation: Image variation type ("product_in_use" or "installation")
            all_image_urls: List of all product image URLs for multi-reference
            
        Returns:
            str: Base64 data URL of edited image or None if editing fails
        """
        if not self.api_key:
            logger.warning("SeeDream API key not configured")
            return None

        try:
            logger.info(f"🎨 SeeDream: Editing image for: {product_title} (variation: {variation})")

            # Prepare reference images
            reference_urls = all_image_urls if all_image_urls and len(all_image_urls) > 1 else [original_image_url]
            encoded_images = self._download_and_encode_images(reference_urls)
            
            if not encoded_images:
                logger.error("❌ No images could be encoded")
                return None

            # Detect product category for scenario selection
            product_lower = product_title.lower()
            
            # Expanded furniture keywords
            furniture_keywords = [
                'bench', 'chair', 'seat', 'seating', 'table', 'sofa', 'couch', 'stool', 'furniture',
                'lounger', 'hammock', 'swing', 'gazebo', 'pergola', 'planter', 'pot', 'bed',
                'cabinet', 'shelf', 'shelving', 'desk', 'ottoman', 'recliner', 'rocker',
                'loveseat', 'sectional', 'futon', 'daybed', 'chaise'
            ]
            
            # Expanded outdoor/lifestyle keywords
            lifestyle_keywords = [
                'garden', 'outdoor', 'patio', 'deck', 'decking', 'bbq', 'grill', 'fire pit',
                'umbrella', 'parasol', 'fountain', 'statue', 'ornament', 'decorative',
                'home', 'living', 'bedroom', 'dining', 'kitchen', 'bathroom',
                'pool', 'spa', 'hot tub', 'sauna', 'playground', 'play', 'toy',
                'pet', 'dog', 'cat', 'bird', 'aquarium', 'fish tank',
                'lighting', 'lamp', 'chandelier', 'sconce', 'lantern',
                'rug', 'carpet', 'mat', 'cushion', 'pillow', 'throw',
                'curtain', 'blind', 'shade', 'drape',
                'vase', 'bowl', 'basket', 'container', 'storage box',
                'mirror', 'picture frame', 'art', 'wall decor',
                'candle', 'incense', 'diffuser', 'aromatherapy'
            ]
            
            is_furniture = any(keyword in product_lower for keyword in furniture_keywords)
            is_outdoor_lifestyle = any(keyword in product_lower for keyword in lifestyle_keywords)

            if is_furniture or is_outdoor_lifestyle:
                scenario_type = "LIFESTYLE"
                logger.info(f"🏡 Detected LIFESTYLE product: {product_title}")
            else:
                scenario_type = "INDUSTRIAL"
                logger.info(f"🏭 Detected INDUSTRIAL product: {product_title}")

            # Build size context
            size_context = ""
            if len(reference_urls) > 1:
                size_context = f"""📏 SIZE & SCALE CONTEXT:
- You have been provided with {len(reference_urls)} reference images of this product
- Analyze ALL images to understand the product's ACTUAL REAL-WORLD SIZE and proportions
- The product title "{product_title}" indicates the true nature and scale of this product
- PAY CLOSE ATTENTION to size indicators in the images (people, objects, measurements)
- Ensure the generated image shows the product at its CORRECT REAL-WORLD SCALE
- If the product is large (barriers, bollards, parking equipment, industrial items), show it at FULL SIZE
- If the product is small (tools, accessories), show it at appropriate human-scale

🎯 COMPLETE PRODUCT SETUP:
- Study ALL {len(reference_urls)} reference images to see the COMPLETE product setup
- If images show containers/tanks ON a pallet (like IBC Spill Pallets) → show WITH containers
- If images show items IN/ON racks or shelves → show WITH items stored
- If images show equipment WITH accessories or attachments → show COMPLETE assembly
- DO NOT generate just an empty base/frame if references show it loaded or complete
- The reference images show how the product is MEANT TO LOOK - replicate that exactly
"""

            # Generate prompt based on variation
            if variation == "product_in_use":
                # IMAGE 1: White background product shot
                prompt = f"""Professional studio product photography with SEAMLESS pure white background.

PRODUCT TO RECREATE:
{size_context}
Product Name: {product_title}

🎯 CRITICAL: SEAMLESS WHITE BACKGROUND REQUIREMENT
- Background must be COMPLETELY UNIFORM PURE WHITE (#FFFFFF or RGB 255,255,255)
- Absolutely NO circular halos, vignettes, or white circles around the product
- NO sunlight
- NO shadows, gradients, gray tones, or darker edges anywhere on the background
- NO visible floor, surface, or ground line - product appears to float
- Background must be ONE SOLID COLOR - pure white from edge to edge
- Clean, seamless white backdrop like professional Amazon/Apple product photography
- The ENTIRE background must be the EXACT SAME white - no variations

⚠️ CRITICAL: AVOID THESE COMMON ARTIFACTS
- NO white circular glow or halo effect around the product
- NO vignetting (darker edges fading to white center)
- NO drop shadows or contact shadows on the white background
- NO visible surface beneath the product
- NO gradient transitions anywhere in the background
- The white background should be absolutely uniform with no variations

📸 STUDIO SETUP:
- Professional infinity cove photography studio with seamless white cyclorama
- Uniform high-key lighting completely eliminating all background shadows
- Product isolated on pure white with perfect edge blending
- NO visible floor, NO horizon line, NO surface texture
- Background completely blown out to pure white (#FFFFFF)
- Advanced photo editing to ensure 100% uniform white background

🔒 PRODUCT RECREATION (EXACT MATCH):
Based on the reference images provided, recreate this product with PERFECT ACCURACY:
- Exact colors and materials as shown
- Exact shape, form, and structure
- All physical features, buttons, grooves, edges, patterns
- Correct proportions and dimensions
- Complete product setup (if it holds items, show it loaded/functional)
- Remove ALL text, logos, branding, labels
- Product edges should be clean and well-defined against white

🚫 WHAT NOT TO INCLUDE:
- NO people, hands, or body parts
- NO environment, floor, surfaces, or ground
- NO shadows, halos, or any artifacts on the white background
- NO circular white glow around the product
- NO props or additional objects
- NO text or branding on product
- NO visible floor line or horizon

📸 COMPOSITION & ANGLE:
- Product perfectly centered in frame
- Fills 70-80% of the image
- Slight 3/4 angle view to show depth and dimension
- All key features clearly visible
- Professional e-commerce photography composition
- Product appears to float on pure white

💡 LIGHTING:
- Bright, even lighting across entire product
- Soft shadows ON THE PRODUCT ITSELF ONLY for dimension (showing product form)
- ZERO shadows on the background - background must be pure white
- High-key lighting that completely blows out background to white
- Professional studio quality with perfect white balance

🎯 FINAL RESULT:
A pristine, professional product photograph with COMPLETELY SEAMLESS PURE WHITE BACKGROUND - exactly like high-end e-commerce product listings (Amazon, Apple, etc.). The product should appear to cleanly float on a uniform white background with ZERO artifacts, halos, shadows, or variations. The background must be ONE SOLID WHITE COLOR from edge to edge with no circular halos or vignettes."""

            else:
                # IMAGE 2: Installation/lifestyle scene
                prompt = f"""You are a professional lifestyle product photographer. Transform this product image into a compelling, real-world application photograph showing the product in use.

PRODUCT: {product_title}
{size_context}

🎯 PHOTOGRAPHY OBJECTIVE:
Create a REALISTIC, professional photograph showing this product being used in its INTENDED REAL-WORLD APPLICATION.
The product SIZE and SCALE must be ACCURATE based on the product title and reference images provided.

⚠️ CRITICAL: PRESERVE THE EXACT PRODUCT APPEARANCE
🔒 PRODUCT INTEGRITY - MUST NOT CHANGE:
1. Keep the product's EXACT PHYSICAL DESIGN - do not alter shape, form, or structure
2. Preserve EXACT COLORS - maintain all original colors of the product precisely
3. Keep EXACT MATERIALS and textures - metal stays metal, plastic stays plastic, etc.
4. Maintain EXACT DIMENSIONS and proportions as shown in reference images
5. Keep ALL PHYSICAL FEATURES - buttons, grooves, edges, patterns exactly as they are
6. Do NOT redesign, modify, or "improve" the product in any way
7. The product must be IDENTICAL to the original - only remove text/logos/brands

✅ WHAT YOU CAN CHANGE:
- The ENVIRONMENT and background (add realistic workplace/lifestyle setting)
- The LIGHTING and photography angle
- Add PEOPLE interacting with the product (hands, workers, users)
- Add CONTEXT objects (tools, vehicles, other environmental items)
- The SCENARIO showing how the product is used

❌ WHAT YOU CANNOT CHANGE:
- The product's physical appearance, design, or features
- The product's colors or materials
- The product's size or proportions
- The product's shape or structure

🎯 RESULT: The SAME product in a NEW realistic environment/scenario

SCENARIO TYPE: {scenario_type}

👤 HUMAN INTERACTION:
{("LIFESTYLE SCENARIO - Natural, Relaxed Usage:" if scenario_type == "LIFESTYLE" else "ACTIVE USE SCENARIO - Installation/Operation:")}
{("- Show person naturally using or enjoying the product (sitting, relaxing, etc.)" if scenario_type == "LIFESTYLE" else "- Show professional worker, craftsman, or user actively installing or operating the product")}
{("- Person dressed casually and comfortably for the setting" if scenario_type == "LIFESTYLE" else "- Person dressed appropriately (safety gear, work clothes, etc.)")}
{("- Natural, relaxed posture - enjoying the product" if scenario_type == "LIFESTYLE" else "- Focus on HANDS and product interaction - holding, installing, operating")}
{("- Person can be partially visible or in background" if scenario_type == "LIFESTYLE" else "- Person's face can be partially visible or out of focus")}
{("- Authentic lifestyle moment captured naturally" if scenario_type == "LIFESTYLE" else "- Natural, authentic body language and realistic usage posture")}

🏗️ ENVIRONMENT & SETTING:
{("LIFESTYLE SETTING - Beautiful, Natural Environment:" if scenario_type == "LIFESTYLE" else "WORKPLACE SETTING - Authentic Work Environment:")}
{("- Outdoor garden, patio, deck, backyard, or beautiful home setting" if scenario_type == "LIFESTYLE" else "- Job site, workshop, garage, construction area, or workplace")}
{("- Lush greenery, flowers, natural landscaping in background (softly blurred)" if scenario_type == "LIFESTYLE" else "- Work surfaces, tools, equipment, materials in background (blurred)")}
{("- Natural sunlight, golden hour lighting, or soft outdoor illumination" if scenario_type == "LIFESTYLE" else "- Workshop lighting, natural daylight, or work environment lighting")}
{("- Well-maintained, inviting outdoor or home environment" if scenario_type == "LIFESTYLE" else "- Realistic workplace with authentic surfaces (concrete, metal, wood)")}
{("- NO workplace signage needed - pure lifestyle aesthetic" if scenario_type == "LIFESTYLE" else "- Optional: Safety signs in background (CAUTION, WARNING, EXIT) for authenticity")}

📸 PROFESSIONAL PHOTOGRAPHY QUALITY:
1. Photorealistic, looks like actual {("lifestyle magazine" if scenario_type == "LIFESTYLE" else "documentary-style")} product photography
2. Natural lighting appropriate to the environment
3. Shallow depth of field - product and person in focus, background beautifully blurred
4. Professional color grading with authentic, natural tones
5. {("Inviting, aspirational composition showing desirable lifestyle" if scenario_type == "LIFESTYLE" else "Dynamic composition showing action, movement, or active use")}
6. Camera angle: Eye-level or slightly above, showing product in perfect context

🎨 REALISM & AUTHENTICITY:
1. Must look like a REAL PHOTOGRAPH, not CGI or artificial
2. Natural textures, authentic materials
3. {("Beautiful, well-maintained environment - NOT overly perfect, naturally inviting" if scenario_type == "LIFESTYLE" else "Genuine work environment - NOT overly clean or staged")}
4. Realistic lighting with natural shadows
5. Authentic product proportions and scale relative to human body

🚫 BRAND & LOGO REMOVAL - CRITICAL:
1. Remove ALL text from the PRODUCT itself:
   - Brand names, model numbers, manufacturer marks, logos
   - Product labels, serial numbers, company names
   - Replace with CLEAN surfaces matching the product's material
   - The product must be completely TEXT-FREE and BRAND-FREE

2. KEEP realistic environmental text for authenticity:
   ✅ KEEP: Safety signs ("DANGER", "CAUTION", "WARNING", "SAFETY FIRST")
   ✅ KEEP: Directional signs ("EXIT", "ENTRANCE", "UP", "DOWN")
   ✅ KEEP: Generic workplace signage ("FIRE EXTINGUISHER", "FIRST AID")

3. REMOVE from environment:
   ❌ REMOVE: Company names, business logos, brand names
   ❌ REMOVE: Specific company signage or branded posters
   ❌ REMOVE: Manufacturer logos on background equipment

✅ WHAT TO SHOW:
1. Product in ACTIVE USE or being handled/installed
2. Appropriate human interaction (hands holding, using, installing)
3. Real-world application environment
4. Natural, realistic usage scenario
5. Professional, engaging composition that tells a story

🎯 FINAL RESULT:
A compelling, photorealistic lifestyle image showing the product being used in its intended real-world application, with appropriate human interaction and environment - professional, authentic, engaging, and completely text-free."""

            # Prepare API payload
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "prompt": prompt,
                "image": encoded_images,
                "strength": 0.7,
                "guidance_scale": 7.5,
                "height":"2048",
                "widht": "2048",
                "num_images": 1
            }

            logger.info(f"🚀 Sending request to SeeDream API...")
            logger.info(f"   Model: {self.model}")
            logger.info(f"   Variation: {variation}")
            logger.info(f"   Reference images: {len(encoded_images)}")

            # Retry logic for timeout errors
            max_retries = 2
            timeout_seconds = 180  # Increased to 3 minutes
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"   Attempt {attempt + 1}/{max_retries}...")
                    response = requests.post(self.base_url, json=payload, headers=headers, timeout=timeout_seconds)
                    
                    if response.status_code != 200:
                        logger.error(f"❌ SeeDream API error: {response.status_code} - {response.text}")
                        if attempt < max_retries - 1:
                            logger.info(f"   Retrying in 5 seconds...")
                            import time
                            time.sleep(5)
                            continue
                        return None
                    
                    # Success - break out of retry loop
                    break
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⏱️ Request timed out after {timeout_seconds}s (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        logger.info(f"   Retrying with fresh connection...")
                        import time
                        time.sleep(5)
                        continue
                    else:
                        logger.error(f"❌ All retry attempts failed - SeeDream API timeout")
                        return None
                except requests.exceptions.RequestException as e:
                    logger.error(f"❌ Request error: {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"   Retrying...")
                        import time
                        time.sleep(5)
                        continue
                    return None

            data = response.json()

            # Extract image from response
            # Format 1: Direct images array with b64_json
            if "images" in data and data["images"]:
                for img in data["images"]:
                    if isinstance(img, dict) and "b64_json" in img:
                        image_base64 = img["b64_json"]
                        data_url = f"data:image/png;base64,{image_base64}"
                        logger.info(f"✅ SeeDream: Successfully edited image (variation: {variation})")
                        return data_url
                    elif isinstance(img, str):
                        data_url = f"data:image/png;base64,{img}"
                        logger.info(f"✅ SeeDream: Successfully edited image (variation: {variation})")
                        return data_url

            # Format 2: Data array with images
            elif "data" in data and data["data"]:
                for img in data["data"]:
                    if isinstance(img, dict) and "b64_json" in img:
                        image_base64 = img["b64_json"]
                        data_url = f"data:image/png;base64,{image_base64}"
                        logger.info(f"✅ SeeDream: Successfully edited image (variation: {variation})")
                        return data_url
                    elif isinstance(img, dict) and "url" in img:
                        # Download from URL and convert to base64
                        img_data = requests.get(img["url"]).content
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        data_url = f"data:image/png;base64,{img_base64}"
                        logger.info(f"✅ SeeDream: Successfully edited image from URL (variation: {variation})")
                        return data_url

            logger.error(f"❌ No image found in SeeDream response. Response keys: {list(data.keys())}")
            return None

        except Exception as e:
            logger.error(f"❌ Error editing image with SeeDream: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
