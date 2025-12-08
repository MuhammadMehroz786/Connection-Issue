"""
Flux (Black Forest Labs) Image Generation Service
Handles image generation using Flux API
"""

import requests
import logging
import base64
import io
from PIL import Image

logger = logging.getLogger(__name__)


class FluxService:
    """Service for generating images using Flux (Black Forest Labs) API"""

    def __init__(self, api_key):
        """
        Initialize Flux service
        
        Args:
            api_key: Black Forest Labs API key
        """
        self.api_key = api_key
        self.base_url = "https://api.bfl.ai/v1"  
        
        if not self.api_key:
            logger.warning("⚠️ No Flux API key provided")
        else:
            logger.info("✅ Flux service initialized")

    def generate_product_image(self, prompt, product_title, width=1024, height=1024):
        """
        Generate a product image using Flux API
        
        Args:
            prompt: The prompt for image generation
            product_title: Product title for context
            width: Image width (default 1024)
            height: Image height (default 1024)
            
        Returns:
            str: Base64 data URL of generated image or None if generation fails
        """
        if not self.api_key:
            logger.warning("Flux API key not configured")
            return None

        try:
            logger.info(f"🎨 Flux: Generating image for: {product_title}")
            logger.info(f"   Prompt: {prompt[:150]}...")

            # Flux API endpoint for image generation
            url = f"{self.base_url}/flux-2-pro"
            
            headers = {
                "Content-Type": "application/json",
                "X-Key": self.api_key
            }
            
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "prompt_upsampling": False,
                "safety_tolerance": 2,
                "output_format": "jpeg"
            }

            # Request image generation
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Get the task ID
            task_id = result.get('id')
            if not task_id:
                logger.error("❌ No task ID returned from Flux API")
                return None
            
            logger.info(f"✅ Flux: Task created - {task_id}, waiting for result...")
            
            # Poll for result
            result_url = f"{self.base_url}/get_result"
            max_attempts = 60  # 60 attempts with 2 second intervals = 2 minutes max
            
            for attempt in range(max_attempts):
                import time
                time.sleep(2)  # Wait 2 seconds between polls
                
                result_response = requests.get(
                    result_url,
                    params={"id": task_id},
                    headers=headers,
                    timeout=30
                )
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    status = result_data.get('status')
                    
                    if status == 'Ready':
                        # Get the image URL
                        image_url = result_data.get('result', {}).get('sample')
                        if not image_url:
                            logger.error("❌ No image URL in Flux response")
                            return None
                        
                        # Download the generated image
                        img_response = requests.get(image_url, timeout=30)
                        img_response.raise_for_status()
                        image_data = img_response.content
                        
                        # Load and crop to 1:1 aspect ratio
                        img = Image.open(io.BytesIO(image_data))
                        # Convert palette mode (P) or other modes to RGB for JPEG compatibility
                        if img.mode not in ('RGB', 'L'):
                            logger.info(f"📸 Converting image from {img.mode} mode to RGB")
                            img = img.convert('RGB')

                        width, height = img.size

                        if width != height:
                            size = min(width, height)
                            left = (width - size) // 2
                            top = (height - size) // 2
                            img = img.crop((left, top, left + size, top + size))
                            logger.info(f"📐 Cropped image to 1:1 aspect ratio: {size}x{size}px")

                        # Convert to base64 data URL
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG", quality=95)
                        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        data_url = f"data:image/jpeg;base64,{img_base64}"
                        
                        logger.info(f"✅ Flux: Successfully generated image for: {product_title}")
                        return data_url
                    
                    elif status == 'Error':
                        error_msg = result_data.get('result', {}).get('error', 'Unknown error')
                        logger.error(f"❌ Flux generation failed: {error_msg}")
                        return None
                    
                    # Still processing, continue polling
                    if attempt % 5 == 0:
                        logger.info(f"⏳ Flux: Still generating... (attempt {attempt + 1}/{max_attempts})")
            
            logger.error(f"❌ Flux: Timeout waiting for image generation")
            return None

        except requests.exceptions.Timeout:
            logger.error(f"❌ Flux API timeout for: {product_title}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Flux API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error generating image with Flux: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None

    def _get_edit_instructions(self, variation):
        """
        Get image editing instructions - EXACT SAME as Gemini service
        """
        instructions = {
            "product_in_use": """
📸 IMAGE 1: PRODUCT IN USE (CLEAN, PROFESSIONAL, NO WORKERS)

🎯 OBJECTIVE:
Create a clean, professional product image showing the product in its intended use ALREADY INSTALLED and functioning as designed.

⚠️ CRITICAL: NO WORKERS, NO HANDS, NO TOOLS visible in this image.

🔒 PRESERVE EXACT PRODUCT APPEARANCE:
- The product itself must remain IDENTICAL to the original reference images
- Do NOT change the product's color, shape, size, design, or any physical features
- ONLY change the environment/background/context around the product
- The product is perfect as-is - DO NOT redesign or modify it

📸 CRITICAL: SHOW COMPLETE PRODUCT AS SEEN IN REFERENCE IMAGES:
- Study ALL reference images to see how the product is MEANT to be shown
- If reference images show containers ON pallets → show containers ON pallet
- If reference images show items IN/ON racks → show items stored properly
- If reference images show equipment WITH accessories → show complete setup
- DO NOT show just the base/frame if reference images show complete assembly
- The reference images are your guide - replicate the COMPLETE setup you see

🔧 PRODUCT PRESENTATION:
- Show the product ALREADY INSTALLED and in use
- Product functioning as designed in its final, installed state
- COMPLETE SETUP as shown in reference images (not just base/empty structure)
- Clean, professional presentation
- Product should look like it's being used, but WITHOUT people visibly interacting with it
- The SAME EXACT COMPLETE product from the reference images, just in a real-world setting

🌍 ENVIRONMENT & CONTEXT:
- Realistic environment relevant to the product
- Use realistic lighting and correct scale
- Clean, well-maintained environment
- Include ONLY objects necessary to show the product's purpose

📸 COMPOSITION:
- Professional, catalog-quality photography
- Straight-on or slight angle to show product clearly
- Natural, appropriate lighting for the environment
- Sharp focus on product
- Clean, uncluttered background

🚫 WHAT NOT TO SHOW:
- NO workers or people
- NO hands touching the product
- NO tools or installation equipment
- NO installation process

🚫 BRANDING:
- NO brand names, logos, or text on the product
- NO company signage or branded materials
- Clean surfaces only

🎯 FINAL RESULT:
A professional, clean image showing the product already installed and serving its purpose, photographed as if for a high-quality product catalog.
""",
            "installation": """
📸 IMAGE 2: REAL-LIFE APPLICATION (PRODUCT IN ACTUAL USE)

🎯 OBJECTIVE:
Show the product being used in a REAL-LIFE APPLICATION - how it actually functions in the real world.
This is NOT an installation scene - this shows the product DOING ITS JOB.

🎯 WHAT TO SHOW:
Analyze the product title and reference images to understand its PURPOSE, then show it fulfilling that purpose:

Examples by product type:
- IBC Spill Pallet → Show in chemical storage area/warehouse with IBC container on top, realistic workplace setting
- Parking Bollard → Show installed in parking lot protecting area, cars nearby, real parking environment
- Wheel Stop → Show in parking space with vehicle wheel against it
- Safety Barrier → Show protecting hazard area in active workplace
- Floor Tape/Markers → Show applied on floor with workplace activity (people walking, forklifts, etc.)
- Storage Rack → Show in warehouse with items stored, realistic facility
- Speed Bump → Show installed on road/driveway with vehicles
- Sign/Post → Show in its intended location serving its warning/direction purpose

🎯 KEY PRINCIPLE: FUNCTION OVER INSTALLATION
- Show the product WORKING, not being installed
- Show the product SERVING ITS PURPOSE in its natural environment
- The viewer should understand WHY this product exists and what it does

🔒 PRESERVE EXACT PRODUCT APPEARANCE:
- The product being installed must be IDENTICAL to the original reference images
- Do NOT change the product's color, shape, size, design, or any physical features
- ONLY change the environment/scenario around the product (add workers, tools, workplace)
- The product is perfect as-is - DO NOT redesign or modify it
- Show the EXACT SAME product being installed in a realistic workplace setting

📸 CRITICAL: SHOW COMPLETE PRODUCT AS SEEN IN REFERENCE IMAGES:
- Study ALL reference images to understand the COMPLETE product
- If product is designed to HOLD items (pallets, racks, stands):
  * Show the COMPLETE setup - the base product WITH what it's meant to hold
  * IBC pallet → Show WITH IBC container on top
  * Storage rack → Show WITH items stored on shelves
  * Tool holder → Show WITH tools in place
- Show the product LOADED and FUNCTIONAL as it would be in real use
- DO NOT show just an empty base/frame if it's meant to hold something

👥 PEOPLE IN THE SCENE (OPTIONAL - USE ONLY IF IT ADDS CONTEXT):
- People are OPTIONAL, not required - only include if it helps show the application
- If people are shown, they should be:
  * In the background or periphery, not the focus
  * Using/interacting with the area where product is (walking on marked floor, parking near bollard, etc.)
  * Dressed appropriately for the setting (work clothes, safety gear if needed)
  * Natural and authentic, not posed
- For most products, NO people needed - just show the product working in its environment

🌍 REAL-LIFE ENVIRONMENT:
Choose the authentic environment where this product would actually be used:
- Pallets/IBCs → Chemical storage area, warehouse, outdoor containment area
- Parking equipment (bollards, wheel stops, speed bumps) → Parking lots, driveways, roads
- Storage/racks → Warehouses, facilities, organized storage areas
- Safety equipment (barriers, tape, signs) → Active workplaces, construction sites, facilities
- Floor markings → Warehouse floors with forklifts/activity, parking areas

Show realistic context:
- Other relevant equipment in background (forklifts, vehicles, machinery, shelving)
- Proper workplace setting (concrete floors, industrial lighting, outdoor paving)
- Active environment that shows the product is needed and functional
- NOT studio setting - real workplace or outdoor location

📸 COMPOSITION & STYLE:
- Professional industrial/commercial photography
- Documentary-style showing real-world application
- Wide or medium shot that shows product AND its working environment
- Natural lighting appropriate to the setting (warehouse lights, outdoor daylight)
- Focus on the product serving its purpose
- Authentic, not overly staged or perfect

🚫 BRANDING:
- NO brand names or logos on product
- NO company signage in environment
- NO text except generic safety markings if appropriate for setting

🎯 FINAL RESULT:
A professional photograph showing the product in REAL-LIFE APPLICATION - actively serving its purpose in its natural environment. The viewer should clearly understand what this product does and why it's useful. Show the COMPLETE product (loaded/functional) in an authentic workplace or outdoor setting that demonstrates its real-world use case.

Examples of final results:
- IBC Spill Pallet → In warehouse with IBC container on top, chemical storage setting
- Parking Bollard → Installed in parking lot, protecting area, cars visible
- Floor Tape → Applied on warehouse floor, active workplace environment
- Storage Rack → In facility with items stored, realistic warehouse setting
""",
            "application": """
📸 IMAGE 2: PRODUCT APPLICATION (HANDS APPLYING/USING THE PRODUCT)

🎯 OBJECTIVE:
Create a realistic scene showing someone actively APPLYING or USING this product in its intended way - appropriate for small items, markers, tape, paint, labels, accessories, etc.

🔒 PRESERVE EXACT PRODUCT APPEARANCE:
- The product being used must be IDENTICAL to the original reference images
- Do NOT change the product's color, shape, size, design, or any physical features
- ONLY show the product being used/applied in a realistic scenario
- The product is perfect as-is - DO NOT redesign or modify it

🤲 HANDS & APPLICATION:
- Show HANDS actively applying, using, or handling the product
- Hands should be in close-up, clearly showing the application process
- Natural, realistic hand positioning for the specific product type
- Hands can be wearing work gloves if appropriate (e.g., for industrial markers, tape)
- Focus on the APPLICATION ACTION - peeling tape, marking floors, applying labels, etc.

🔧 APPLICATION SCENARIOS BY PRODUCT TYPE:
For FLOOR MARKERS / TAPE / LINES:
- Show hands applying the marker/tape to a floor surface
- Display the application process (peeling backing, pressing down, smoothing)
- Show partially applied product to demonstrate usage
- Realistic floor surface (concrete, asphalt, warehouse floor)

For PAINT / COATING / SPRAY:
- Show hands applying paint to appropriate surface
- May include brush, roller, or spray application
- Show product container/can being used
- Realistic application surface

For LABELS / STICKERS / SIGNS:
- Show hands peeling and applying label
- Display backing being removed
- Show application to relevant surface (box, equipment, wall)

For SMALL TOOLS / ACCESSORIES:
- Show hands using the tool/accessory for its intended purpose
- Demonstrate proper handling and usage
- Include any objects the tool interacts with

For SAFETY / PPE ITEMS:
- Show hands putting on, adjusting, or using the safety item
- Demonstrate proper usage/placement
- Show on appropriate body part or location

🌍 ENVIRONMENT & SURFACE:
- Realistic environment for the product's use case
- Appropriate surface (floor, wall, equipment, package, etc.)
- Clean, professional setting
- Natural or workplace lighting
- Close-up/macro shot to show detail

📸 COMPOSITION & STYLE:
- Close-up, detail-focused photography
- Hands-on demonstration style
- Clear view of the product being applied/used
- Professional instructional/tutorial photo quality
- Sharp focus on hands and product
- Background slightly blurred to emphasize action

🚫 WHAT NOT TO SHOW:
- NO heavy machinery or power tools (drills, saws, etc.) unless product specifically requires them
- NO workers in full high-vis gear (just hands, maybe gloves)
- NO installation equipment inappropriate for the product
- NO construction site setting for small/simple products
- Just hands + product + application surface

🚫 BRANDING:
- NO brand names or logos on product
- NO company signage or branded materials
- Clean product surfaces only

🎯 FINAL RESULT:
A professional, close-up demonstration photo showing hands actively applying or using the product in its real-world application - clear, instructional, and contextually appropriate for the specific product type.
"""
        }
        return instructions.get(variation, instructions["product_in_use"])

    def edit_product_image(self, original_image_url, product_title, variation="main", all_image_urls=None):
        """
        Edit product image using Flux image-to-image (similar to Gemini)
        1. Download the original product image
        2. Create appropriate prompt based on variation (Image 1: white background, Image 2: installation)
        3. Flux generates the edited image using image-to-image
        """
        try:
            logger.info(f"🎨 Flux: Editing image for: {product_title} (variation: {variation})")

            # Step 1: Get the image data (handle both URLs and data URLs)
            try:
                if original_image_url.startswith('data:image'):
                    # It's a data URL (base64) - decode it
                    logger.info(f"   Input: Data URL (base64 encoded image)")
                    # Extract base64 data after the comma
                    base64_data = original_image_url.split(',', 1)[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    # It's a regular URL - download it
                    logger.info(f"   Input: URL - {original_image_url[:100]}...")
                    response = requests.get(original_image_url, timeout=10)
                    response.raise_for_status()
                    image_data = response.content
            except Exception as e:
                logger.error(f"❌ Failed to get image: {str(e)}")
                return None

            # Load and crop to 1:1 aspect ratio
            try:
                img = Image.open(io.BytesIO(image_data))
                # Convert palette mode (P) or other modes to RGB for JPEG compatibility
                if img.mode not in ('RGB', 'L'):
                    logger.info(f"📸 Converting image from {img.mode} mode to RGB")
                    img = img.convert('RGB')
            except Exception as e:
                logger.error(f"❌ Cannot open image: {str(e)}")
                return None

            width, height = img.size
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                logger.info(f"📐 Cropped image to 1:1 aspect ratio: {size}x{size}px")

            # Get variation-specific edit instructions (same as Gemini)
            edit_instructions = self._get_edit_instructions(variation)

            # Detect product category for smart scenario selection (same as Gemini)
            product_lower = product_title.lower()
            is_furniture = any(keyword in product_lower for keyword in [
                'bench', 'chair', 'seat', 'table', 'sofa', 'couch', 'stool', 'furniture',
                'lounger', 'hammock', 'swing', 'gazebo', 'pergola', 'planter', 'pot'
            ])
            is_outdoor_lifestyle = any(keyword in product_lower for keyword in [
                'garden', 'outdoor', 'patio', 'deck', 'bbq', 'grill', 'fire pit',
                'umbrella', 'parasol', 'fountain', 'statue', 'ornament'
            ])

            # Choose appropriate scenario based on product type (same as Gemini)
            if is_furniture or is_outdoor_lifestyle:
                scenario_type = "LIFESTYLE"
            else:
                scenario_type = "INDUSTRIAL"

            # Step 2: Create appropriate prompt based on variation
            size_context = ""
            if all_image_urls and len(all_image_urls) > 1:
                size_context = f"""
📏 SIZE & SCALE CONTEXT:
- You have {len(all_image_urls)} reference images of this product
- The product title "{product_title}" indicates the true nature and scale of this product
- Ensure the generated image shows the product at its CORRECT REAL-WORLD SCALE
"""

            if variation == "product_in_use":
                # IMAGE 1: Clean product shot with white background
                flux_prompt = f"""Professional studio product photography on pure white background.

PRODUCT: {product_title}
{size_context}

🎯 CRITICAL: USE THE PROVIDED REFERENCE IMAGE AS YOUR GUIDE
The input image shows the ACTUAL product. Study it carefully to understand:
- The exact physical design, shape, and structure
- All color details, materials, and finishes
- Product features, components, and how they connect
- Complete product assembly (if it has multiple parts)
- Product scale and proportions

Your task: Recreate this EXACT product on a pure white background.

🎯 CRITICAL: WHITE BACKGROUND REQUIREMENT
- Background must be PURE WHITE (#FFFFFF)
- Absolutely NO shadows on the background
- NO gradients, NO gray tones
- Clean, seamless white backdrop like professional studio photography
- Think Amazon product listing or Apple product photography style

📸 STUDIO SETUP:
- Professional photography studio with white cyclorama backdrop
- Soft box lighting from multiple angles to eliminate shadows
- Product floating on pure white, no visible surface
- High-key lighting setup for clean white background
- No floor shadows, no background texture

🔒 PRODUCT RECREATION (EXACT MATCH TO REFERENCE IMAGE):
Study the input reference image and recreate this EXACT product:
- EXACT colors from reference - match every color precisely (reds, yellows, blacks, blues, etc.)
- EXACT shape and form - copy the structure exactly as shown
- EXACT materials and finishes (metal, plastic, rubber, fabric, etc.)
- ALL physical features visible in reference (buttons, grooves, edges, patterns, holes, markings)
- EXACT proportions and dimensions relative to other parts
- Complete product setup exactly as shown in reference:
  * If reference shows containers/items ON something → include them
  * If reference shows products IN/ON racks → show complete setup
  * If reference shows equipment WITH accessories → show full assembly
  * Match the COMPLETENESS level of the reference image
- Remove ALL text, logos, branding, labels (keep surfaces clean but maintain color/material)

⚠️ CRITICAL MATCHING REQUIREMENTS:
1. COLOR ACCURACY: Match EVERY color from the reference image exactly
   - If reference shows yellow safety bars → use that exact yellow
   - If reference shows black components → use that exact black
   - If reference shows red accents → use that exact red
   - Preserve color combinations and patterns exactly

2. STRUCTURAL ACCURACY: Copy the exact form and assembly
   - Count components in reference and include all of them
   - Match how parts connect and attach to each other
   - Preserve spacing, gaps, and dimensional relationships
   - Copy surface details (perforations, grating, mesh, etc.)

3. MATERIAL ACCURACY: Match textures and finishes
   - Metal surfaces → show appropriate metallic sheen
   - Plastic → show appropriate plastic finish (matte/glossy)
   - Rubber → show rubber texture
   - Fabric → show fabric weave/texture

4. COMPLETENESS: Match the assembly level shown in reference
   - If reference shows a loaded/functional product → show it loaded
   - If reference shows accessories attached → include them
   - If reference shows stacked items → show the stack
   - Don't show empty structures if reference shows them full/loaded

🚫 WHAT NOT TO INCLUDE:
- NO people, hands, or body parts
- NO environment, floor, or surfaces
- NO shadows on the white background
- NO props or additional objects beyond what's in the reference
- NO text or branding on product

📸 COMPOSITION & ANGLE:
- Product centered in frame
- Fills 70-80% of the image
- Slight 3/4 angle view to show depth and dimension (similar to reference angle)
- All key features clearly visible
- Professional e-commerce photography composition

💡 LIGHTING:
- Bright, even lighting across entire product
- Soft shadows on product itself for dimension (but NOT on background)
- High-key lighting for pure white background
- Professional studio quality
- Lighting reveals all material details and colors accurately

🎯 FINAL RESULT:
A pristine, professional product photograph on PURE WHITE BACKGROUND showing the EXACT product from the reference image with perfect color matching, structural accuracy, and material representation - exactly like high-end e-commerce product listings (Amazon, Apple, etc.). The product should appear to float on white with perfect lighting and zero background shadows, but must be IDENTICAL to the reference product in every visual detail."""

            else:
                # IMAGE 2: Installation/working scenario
                flux_prompt = f"""Professional product photography showing real-world installation and usage.

🎯 CRITICAL: USE THE PROVIDED IMAGE AS YOUR EXACT REFERENCE
The input image shows the EXACT product you must recreate. This is Image 1 (white background product shot).

PRODUCT: {product_title}
{size_context}
{edit_instructions}

🎯 PHOTOGRAPHY OBJECTIVE:
Create a REALISTIC, professional photograph showing this product being used in its INTENDED REAL-WORLD APPLICATION.
The product SIZE and SCALE must be ACCURATE based on the product title and reference images provided.

⚠️ CRITICAL: PRESERVE THE EXACT PRODUCT APPEARANCE FROM IMAGE 1
🔒 PRODUCT INTEGRITY - MUST NOT CHANGE:
**YOU ARE TRANSFORMING THE BACKGROUND/ENVIRONMENT ONLY - THE PRODUCT ITSELF MUST REMAIN 100% IDENTICAL TO IMAGE 1**

1. Study the input image (Image 1) carefully - this shows the EXACT product
2. Keep the product's EXACT PHYSICAL DESIGN from Image 1 - do not alter shape, form, or structure
3. Preserve EXACT COLORS from Image 1 - maintain all original colors of the product precisely
4. Keep EXACT MATERIALS and textures from Image 1 - metal stays metal, plastic stays plastic, etc.
5. Maintain EXACT DIMENSIONS and proportions as shown in Image 1
6. Keep ALL PHYSICAL FEATURES from Image 1 - buttons, grooves, edges, patterns, surface details exactly as they are
7. Copy every detail, marking, feature, and characteristic from Image 1
8. Do NOT redesign, modify, or "improve" the product in any way
9. The product must be PIXEL-PERFECT IDENTICAL to Image 1 - only the background/environment changes

🎯 YOUR TASK:
- Take the EXACT product from Image 1 (white background)
- Place it in a new realistic environment/scenario
- Keep the product 100% identical - only change what's around it

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
{"LIFESTYLE SCENARIO - Natural, Relaxed Usage:" if scenario_type == "LIFESTYLE" else "ACTIVE USE SCENARIO - Installation/Operation:"}
{"- Show person naturally using or enjoying the product (sitting, relaxing, etc.)" if scenario_type == "LIFESTYLE" else "- Show professional worker, craftsman, or user actively installing or operating the product"}
{"- Person dressed casually and comfortably for the setting" if scenario_type == "LIFESTYLE" else "- Person dressed appropriately (safety gear, work clothes, etc.)"}
{"- Natural, relaxed posture - enjoying the product" if scenario_type == "LIFESTYLE" else "- Focus on HANDS and product interaction - holding, installing, operating"}
{"- Person can be partially visible or in background" if scenario_type == "LIFESTYLE" else "- Person's face can be partially visible or out of focus"}
{"- Authentic lifestyle moment captured naturally" if scenario_type == "LIFESTYLE" else "- Natural, authentic body language and realistic usage posture"}

🏗️ ENVIRONMENT & SETTING:
{"LIFESTYLE SETTING - Beautiful, Natural Environment:" if scenario_type == "LIFESTYLE" else "WORKPLACE SETTING - Authentic Work Environment:"}
{"- Outdoor garden, patio, deck, backyard, or beautiful home setting" if scenario_type == "LIFESTYLE" else "- Job site, workshop, garage, construction area, or workplace"}
{"- Lush greenery, flowers, natural landscaping in background (softly blurred)" if scenario_type == "LIFESTYLE" else "- Work surfaces, tools, equipment, materials in background (blurred)"}
{"- Natural sunlight, golden hour lighting, or soft outdoor illumination" if scenario_type == "LIFESTYLE" else "- Workshop lighting, natural daylight, or work environment lighting"}
{"- Well-maintained, inviting outdoor or home environment" if scenario_type == "LIFESTYLE" else "- Realistic workplace with authentic surfaces (concrete, metal, wood)"}
{"- NO workplace signage needed - pure lifestyle aesthetic" if scenario_type == "LIFESTYLE" else "- Optional: Safety signs in background (CAUTION, WARNING, EXIT) for authenticity"}

📸 PROFESSIONAL PHOTOGRAPHY QUALITY:
1. Photorealistic, looks like actual {"lifestyle magazine" if scenario_type == "LIFESTYLE" else "documentary-style"} product photography
2. Natural lighting appropriate to the environment
3. Shallow depth of field - product and person in focus, background beautifully blurred
4. Professional color grading with authentic, natural tones
5. {"Inviting, aspirational composition showing desirable lifestyle" if scenario_type == "LIFESTYLE" else "Dynamic composition showing action, movement, or active use"}
6. Camera angle: Eye-level or slightly above, showing product in perfect context

🎨 REALISM & AUTHENTICITY:
1. Must look like a REAL PHOTOGRAPH, not CGI or artificial
2. Natural textures, authentic materials
3. {"Beautiful, well-maintained environment - NOT overly perfect, naturally inviting" if scenario_type == "LIFESTYLE" else "Genuine work environment - NOT overly clean or staged"}
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

            logger.info(f"🎨 Flux: Generating {'white background product shot' if variation == 'product_in_use' else 'installation/usage scene'}")
            logger.info(f"   Prompt: {flux_prompt[:150]}...")
            
            # Step 3: Call Flux image-to-image API
            if not self.api_key:
                logger.warning("Flux API key not configured")
                return None

            # Convert image to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=95)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Flux API endpoint for image-to-image
            url = f"{self.base_url}/flux-2-pro"
            
            headers = {
                "Content-Type": "application/json",
                "X-Key": self.api_key
            }
            
            payload = {
                "prompt": flux_prompt,
                "image": img_base64,  # Base64 encoded image
                "width": 1024,
                "height": 1024,
                "prompt_upsampling": False,
                "safety_tolerance": 2,
                "output_format": "jpeg"
            }

            # Request image generation
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Get the task ID
            task_id = result.get('id')
            if not task_id:
                logger.error("❌ No task ID returned from Flux API")
                return None
            
            logger.info(f"✅ Flux: Task created - {task_id}, waiting for result...")
            
            # Poll for result
            result_url = f"{self.base_url}/get_result"
            max_attempts = 60  # 60 attempts with 2 second intervals = 2 minutes max
            
            import time
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between polls
                
                result_response = requests.get(
                    result_url,
                    params={"id": task_id},
                    headers=headers,
                    timeout=30
                )
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    status = result_data.get('status')
                    
                    if status == 'Ready':
                        # Get the image URL
                        image_url = result_data.get('result', {}).get('sample')
                        if not image_url:
                            logger.error("❌ No image URL in Flux response")
                            return None
                        
                        # Download the generated image
                        img_response = requests.get(image_url, timeout=30)
                        img_response.raise_for_status()
                        generated_image_data = img_response.content
                        
                        # Convert to base64 data URL
                        generated_img_base64 = base64.b64encode(generated_image_data).decode('utf-8')
                        data_url = f"data:image/jpeg;base64,{generated_img_base64}"
                        
                        logger.info(f"✅ Flux: Successfully edited image (variation: {variation})")
                        return data_url
                    
                    elif status == 'Error':
                        error_msg = result_data.get('result', {}).get('error', 'Unknown error')
                        logger.error(f"❌ Flux generation failed: {error_msg}")
                        return None
                    
                    # Still processing, continue polling
                    if attempt % 5 == 0:
                        logger.info(f"⏳ Flux: Still generating... (attempt {attempt + 1}/{max_attempts})")
            
            logger.error(f"❌ Flux: Timeout waiting for image generation")
            return None

        except Exception as e:
            logger.error(f"❌ Error in Flux edit_product_image: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
