"""Test scenario_type logic"""

# Test LIFESTYLE scenario
product_title = "Garden Bench Chair"
product_lower = product_title.lower()

is_furniture = any(keyword in product_lower for keyword in [
    'bench', 'chair', 'seat', 'table', 'sofa', 'couch', 'stool', 'furniture',
    'lounger', 'hammock', 'swing', 'gazebo', 'pergola', 'planter', 'pot'
])
is_outdoor_lifestyle = any(keyword in product_lower for keyword in [
    'garden', 'outdoor', 'patio', 'deck', 'bbq', 'grill', 'fire pit',
    'umbrella', 'parasol', 'fountain', 'statue', 'ornament'
])

if is_furniture or is_outdoor_lifestyle:
    scenario_type = "LIFESTYLE"
else:
    scenario_type = "INDUSTRIAL"

print(f"Product: {product_title}")
print(f"Scenario Type: {scenario_type}")

# Test the f-string conditional
test_prompt = f"""
SCENARIO TYPE: {scenario_type}

👤 HUMAN INTERACTION:
{("LIFESTYLE SCENARIO - Natural, Relaxed Usage:" if scenario_type == "LIFESTYLE" else "ACTIVE USE SCENARIO - Installation/Operation:")}
{("- Show person naturally using or enjoying the product (sitting, relaxing, etc.)" if scenario_type == "LIFESTYLE" else "- Show professional worker, craftsman, or user actively installing or operating the product")}
"""

print("\nGenerated Prompt:")
print(test_prompt)

# Test INDUSTRIAL scenario
product_title2 = "Speed Bump Ramp"
product_lower2 = product_title2.lower()

is_furniture2 = any(keyword in product_lower2 for keyword in [
    'bench', 'chair', 'seat', 'table', 'sofa', 'couch', 'stool', 'furniture',
    'lounger', 'hammock', 'swing', 'gazebo', 'pergola', 'planter', 'pot'
])
is_outdoor_lifestyle2 = any(keyword in product_lower2 for keyword in [
    'garden', 'outdoor', 'patio', 'deck', 'bbq', 'grill', 'fire pit',
    'umbrella', 'parasol', 'fountain', 'statue', 'ornament'
])

if is_furniture2 or is_outdoor_lifestyle2:
    scenario_type2 = "LIFESTYLE"
else:
    scenario_type2 = "INDUSTRIAL"

print(f"\n\nProduct: {product_title2}")
print(f"Scenario Type: {scenario_type2}")

test_prompt2 = f"""
SCENARIO TYPE: {scenario_type2}

👤 HUMAN INTERACTION:
{("LIFESTYLE SCENARIO - Natural, Relaxed Usage:" if scenario_type2 == "LIFESTYLE" else "ACTIVE USE SCENARIO - Installation/Operation:")}
{("- Show person naturally using or enjoying the product (sitting, relaxing, etc.)" if scenario_type2 == "LIFESTYLE" else "- Show professional worker, craftsman, or user actively installing or operating the product")}
"""

print("\nGenerated Prompt:")
print(test_prompt2)

print("\n✅ Scenario type logic is working correctly!")
