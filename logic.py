import re
import random
import os
from typing import List, Dict, Any
import requests

# Product Catalog Service URL - can be overridden by environment variable
CATALOG_SERVICE_URL = os.getenv("PRODUCT_CATALOGUE_SERVICE_URL", "http://localhost:8082")

def fetch_products_from_catalog() -> List[Dict[str, Any]]:
    """Fetch products from the Product Catalog Service."""
    try:
        # Fetch all products
        response = requests.get(f"{CATALOG_SERVICE_URL}/api/products", params={"size": 100}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Handle paginated response
            if isinstance(data, dict) and "content" in data:
                return data["content"]
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        print(f"Error fetching products from catalog: {e}")
        return get_mock_products()

def get_mock_products() -> List[Dict[str, Any]]:
    """Fallback mock product data if catalog service is unavailable."""
    return [
        {"id": "1", "name": "Intel Core i9-13900K", "subcategory": "CPU", "price": 589.99, "brand": "Intel", "specs": {"socketType": "LGA1700", "wattage": "125"}},
        {"id": "2", "name": "AMD Ryzen 9 7950X", "subcategory": "CPU", "price": 550.00, "brand": "AMD", "specs": {"socketType": "AM5", "wattage": "170"}},
        {"id": "3", "name": "Intel Core i5-13600K", "subcategory": "CPU", "price": 319.99, "brand": "Intel", "specs": {"socketType": "LGA1700", "wattage": "125"}},
        {"id": "4", "name": "NVIDIA GeForce RTX 4090", "subcategory": "GPU", "price": 1599.99, "brand": "NVIDIA", "specs": {"powerRequirement": "450"}},
        {"id": "5", "name": "NVIDIA GeForce RTX 4070", "subcategory": "GPU", "price": 599.99, "brand": "NVIDIA", "specs": {"powerRequirement": "200"}},
        {"id": "6", "name": "ASUS ROG Maximus Z790", "subcategory": "Motherboard", "price": 499.99, "brand": "ASUS", "specs": {"socketType": "LGA1700", "memoryType": "DDR5", "formFactor": "ATX"}},
        {"id": "7", "name": "MSI MAG B650 Tomahawk", "subcategory": "Motherboard", "price": 219.99, "brand": "MSI", "specs": {"socketType": "AM5", "memoryType": "DDR5", "formFactor": "ATX"}},
        {"id": "8", "name": "Corsair Vengeance 32GB DDR5", "subcategory": "RAM", "price": 129.99, "brand": "Corsair", "specs": {"type": "DDR5"}},
        {"id": "9", "name": "Samsung 990 Pro 2TB", "subcategory": "Storage", "price": 169.99, "brand": "Samsung", "specs": {}},
        {"id": "10", "name": "Corsair RM1000x", "subcategory": "PSU", "price": 189.99, "brand": "Corsair", "specs": {"wattage": "1000"}},
        {"id": "11", "name": "Corsair RM750x", "subcategory": "PSU", "price": 119.99, "brand": "Corsair", "specs": {"wattage": "750"}},
        {"id": "12", "name": "NZXT Kraken Z73", "subcategory": "Cooler", "price": 279.99, "brand": "NZXT", "specs": {}},
        {"id": "13", "name": "Lian Li O11 Dynamic", "subcategory": "Case", "price": 149.99, "brand": "Lian Li", "specs": {"formFactor": "ATX"}},
    ]

def generate_build_suggestion(query: str) -> Dict[str, Any]:
    lower_query = query.lower()
    budget = 2000
    build_type = 'gaming'

    # Extract budget
    budget_match = re.search(r'\$?(\d{3,5})', query)
    if budget_match:
        budget = int(budget_match.group(1))

    # Determine build type
    if any(x in lower_query for x in ['workstation', 'video editing', 'content creation']):
        build_type = 'workstation'
    elif any(x in lower_query for x in ['budget', 'cheap', 'affordable']):
        build_type = 'budget'
    elif any(x in lower_query for x in ['4k', 'high-end', 'premium']):
        build_type = 'high-end'

    # Fetch products from catalog service (with fallback to mock)
    products = fetch_products_from_catalog()
    
    # Filter products by subcategory (handle both dict and object-like access)
    def get_subcategory(p):
        if isinstance(p, dict):
            return p.get('subcategory', p.get('subCategory', ''))
        return getattr(p, 'subcategory', getattr(p, 'subCategory', ''))
    
    def get_price(p):
        if isinstance(p, dict):
            return float(p.get('price', p.get('basePrice', 0)))
        return float(getattr(p, 'price', getattr(p, 'basePrice', 0)))
    
    def get_id(p):
        if isinstance(p, dict):
            return str(p.get('id', ''))
        return str(getattr(p, 'id', ''))
    
    def get_name(p):
        if isinstance(p, dict):
            return p.get('name', '')
        return getattr(p, 'name', '')
    
    cpus = [p for p in products if get_subcategory(p) and 'CPU' in get_subcategory(p).upper()]
    gpus = [p for p in products if get_subcategory(p) and 'GPU' in get_subcategory(p).upper()]
    motherboards = [p for p in products if get_subcategory(p) and 'Motherboard' in get_subcategory(p)]
    rams = [p for p in products if get_subcategory(p) and 'RAM' in get_subcategory(p).upper()]
    storage = [p for p in products if get_subcategory(p) and ('Storage' in get_subcategory(p) or 'SSD' in get_subcategory(p) or 'HDD' in get_subcategory(p))]
    psus = [p for p in products if get_subcategory(p) and 'PSU' in get_subcategory(p).upper()]
    coolers = [p for p in products if get_subcategory(p) and ('Cooler' in get_subcategory(p) or 'Cooling' in get_subcategory(p))]
    cases = [p for p in products if get_subcategory(p) and 'Case' in get_subcategory(p)]

    selected_components = []

    # Helper function to safely access product attributes
    def get_product_attr(p, attr, default=None):
        if isinstance(p, dict):
            return p.get(attr, default)
        return getattr(p, attr, default)
    
    def get_spec_value(p, spec_key, default=0):
        specs = get_product_attr(p, 'specs', {})
        if isinstance(specs, dict):
            return specs.get(spec_key, default)
        return getattr(specs, spec_key, default) if hasattr(specs, spec_key) else default

    # Logic adapted from frontend
    if build_type == 'high-end' or budget > 2500:
        selected_components = [
            next((p for p in cpus if get_price(p) > 500), cpus[0] if cpus else None),
            next((p for p in gpus if get_price(p) > 900), gpus[0] if gpus else None),
            next((p for p in motherboards if get_price(p) > 300), motherboards[0] if motherboards else None),
            rams[0] if rams else None,
            storage[0] if storage else None,
            next((p for p in psus if int(get_spec_value(p, 'wattage', 0)) >= 850), psus[0] if psus else None),
            coolers[0] if coolers else None,
            cases[0] if cases else None
        ]
    elif build_type == 'workstation':
        selected_components = [
            next((p for p in cpus if get_product_attr(p, 'brand', '').upper() == 'AMD'), cpus[0] if cpus else None),
            gpus[0] if gpus else None,
            motherboards[0] if motherboards else None,
            rams[0] if rams else None,
            storage[0] if storage else None,
            psus[0] if psus else None,
            coolers[0] if coolers else None,
            cases[0] if cases else None
        ]
    else: # Budget
        selected_components = [
            next((p for p in cpus if get_price(p) < 400), cpus[-1] if cpus else None),
            next((p for p in gpus if get_price(p) < 700), gpus[-1] if gpus else None),
            next((p for p in motherboards if get_price(p) < 250), motherboards[-1] if motherboards else None),
            rams[0] if rams else None,
            storage[0] if storage else None,
            psus[-1] if psus else None,
            coolers[0] if coolers else None,
            cases[0] if cases else None
        ]

    # Filter out None values if any lists were empty
    selected_components = [c for c in selected_components if c]
    
    # Normalize component format for response
    normalized_components = []
    for c in selected_components:
        comp = {
            "id": get_id(c),
            "name": get_name(c),
            "subcategory": get_subcategory(c),
            "price": get_price(c),
            "brand": get_product_attr(c, 'brand', ''),
            "imageUrl": get_product_attr(c, 'imageUrl', get_product_attr(c, 'image_url', '/placeholder-product.png')),
            "specs": get_product_attr(c, 'specs', {})
        }
        normalized_components.append(comp)
    
    total_price = sum(get_price(c) for c in selected_components)

    return {
        "message": f"I've configured a {build_type} build for you based on your budget of ${budget}.",
        "buildSuggestion": {
            "components": normalized_components,
            "totalPrice": total_price
        }
    }

def generate_chat_response(message: str) -> str:
    lower_message = message.lower()
    
    # Fetch products from catalog
    products = fetch_products_from_catalog()
    
    def get_subcategory(p):
        if isinstance(p, dict):
            return p.get('subcategory', p.get('subCategory', ''))
        return getattr(p, 'subcategory', getattr(p, 'subCategory', ''))
    
    def get_name(p):
        if isinstance(p, dict):
            return p.get('name', '')
        return getattr(p, 'name', '')
    
    # Check for product categories
    if 'cpu' in lower_message or 'processor' in lower_message:
        cpu_products = [p for p in products if get_subcategory(p) and 'CPU' in get_subcategory(p).upper()]
        product_names = ", ".join([get_name(p) for p in cpu_products[:3]])
        if product_names:
            return f"We have some great CPUs available, including: {product_names}. Would you like to see more details?"
        return "We have a great selection of CPUs available. Would you like help choosing one for your build?"
        
    if 'gpu' in lower_message or 'graphics card' in lower_message:
        gpu_products = [p for p in products if get_subcategory(p) and 'GPU' in get_subcategory(p).upper()]
        product_names = ", ".join([get_name(p) for p in gpu_products[:3]])
        if product_names:
            return f"Check out our latest GPUs: {product_names}. I can help you find the right one for your build."
        return "We have excellent GPU options available. What are you planning to use your graphics card for?"
        
    if 'motherboard' in lower_message:
        mb_products = [p for p in products if get_subcategory(p) and 'Motherboard' in get_subcategory(p)]
        product_names = ", ".join([get_name(p) for p in mb_products[:3]])
        if product_names:
            return f"We stock top-tier motherboards like: {product_names}."
        return "We have a wide selection of motherboards. What CPU are you planning to use?"
        
    if 'ram' in lower_message or 'memory' in lower_message:
        ram_products = [p for p in products if get_subcategory(p) and 'RAM' in get_subcategory(p).upper()]
        product_names = ", ".join([get_name(p) for p in ram_products[:3]])
        if product_names:
            return f"Upgrade your memory with: {product_names}."
        return "We have various RAM options available. How much memory are you looking for?"

    if 'storage' in lower_message or 'ssd' in lower_message:
        storage_products = [p for p in products if get_subcategory(p) and ('Storage' in get_subcategory(p) or 'SSD' in get_subcategory(p) or 'HDD' in get_subcategory(p))]
        product_names = ", ".join([get_name(p) for p in storage_products[:3]])
        if product_names:
            return f"Fast storage options available: {product_names}."
        return "We have great storage solutions. Are you looking for speed (SSD) or capacity (HDD)?"

    # General help
    if 'help' in lower_message:
        return "I can help you find products like CPUs, GPUs, Motherboards, RAM, and Storage. Just ask me about them!"

    # Default random responses for other queries
    bot_responses = [
        "Thanks for your message! I'm here to help with any questions about our products.",
        "That's a great question! Let me connect you with a specialist who can help.",
        "I'd be happy to help you with that. You can also check out our Help Center for quick answers.",
        "Great choice! Would you like me to help you build a complete system?",
    ]
    return random.choice(bot_responses)
