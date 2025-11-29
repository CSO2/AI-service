import re
import random
from typing import List, Dict, Any

# Mock product data to simulate the catalog. 
# In a production environment, this should be fetched from the Product Catalogue Service.
MOCK_PRODUCTS = [
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

    # Filter products
    cpus = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'CPU']
    gpus = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'GPU']
    motherboards = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Motherboard']
    rams = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'RAM']
    storage = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Storage']
    psus = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'PSU']
    coolers = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Cooler']
    cases = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Case']

    selected_components = []

    # Logic adapted from frontend
    if build_type == 'high-end' or budget > 2500:
        selected_components = [
            next((p for p in cpus if p['price'] > 500), cpus[0]),
            next((p for p in gpus if p['price'] > 900), gpus[0]),
            next((p for p in motherboards if p['price'] > 300), motherboards[0]),
            rams[0], # Simplified
            storage[0],
            next((p for p in psus if int(p['specs'].get('wattage', 0)) >= 850), psus[0]),
            coolers[0],
            cases[0]
        ]
    elif build_type == 'workstation':
        selected_components = [
            next((p for p in cpus if p['brand'] == 'AMD'), cpus[0]),
            gpus[0], # Simplified
            motherboards[0],
            rams[0],
            storage[0],
            psus[0],
            coolers[0],
            cases[0]
        ]
    else: # Budget
        selected_components = [
            next((p for p in cpus if p['price'] < 400), cpus[-1]),
            next((p for p in gpus if p['price'] < 700), gpus[-1]),
            next((p for p in motherboards if p['price'] < 250), motherboards[-1]),
            rams[0],
            storage[0],
            psus[-1],
            coolers[0],
            cases[0]
        ]

    # Filter out None values if any lists were empty
    selected_components = [c for c in selected_components if c]
    
    total_price = sum(c['price'] for c in selected_components)

    return {
        "message": f"I've configured a {build_type} build for you based on your budget of ${budget}.",
        "buildSuggestion": {
            "components": selected_components,
            "totalPrice": total_price
        }
    }

def generate_chat_response(message: str) -> str:
    lower_message = message.lower()
    
    # Check for product categories
    if 'cpu' in lower_message or 'processor' in lower_message:
        products = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'CPU']
        product_names = ", ".join([p['name'] for p in products[:3]])
        return f"We have some great CPUs available, including: {product_names}. Would you like to see more details?"
        
    if 'gpu' in lower_message or 'graphics card' in lower_message:
        products = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'GPU']
        product_names = ", ".join([p['name'] for p in products[:3]])
        return f"Check out our latest GPUs: {product_names}. I can help you find the right one for your build."
        
    if 'motherboard' in lower_message:
        products = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Motherboard']
        product_names = ", ".join([p['name'] for p in products[:3]])
        return f"We stock top-tier motherboards like: {product_names}."
        
    if 'ram' in lower_message or 'memory' in lower_message:
        products = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'RAM']
        product_names = ", ".join([p['name'] for p in products[:3]])
        return f"Upgrade your memory with: {product_names}."

    if 'storage' in lower_message or 'ssd' in lower_message:
        products = [p for p in MOCK_PRODUCTS if p['subcategory'] == 'Storage']
        product_names = ", ".join([p['name'] for p in products[:3]])
        return f"Fast storage options available: {product_names}."

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
