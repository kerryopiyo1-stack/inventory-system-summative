"""
inventory.py

Contains the in-memory inventory store and utility functions for
managing items and querying the OpenFoodFacts API.
"""

import requests
from typing import Dict, List, Optional

# Simulated inventory storage. Each item resembles the OpenFoodFacts API structure.
# This acts as a temporary data store for the app (no persistence).
inventory_data: List[Dict] = [
    {
        "id": 1,
        "barcode": "0038000363238",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "quantity": 12,
        "price": 3.99,
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, natural flavors",
        "status": 1,
    },
    {
        "id": 2,
        "barcode": "041196910495",
        "product_name": "Strawberry Yogurt",
        "brand": "Yoplait",
        "quantity": 20,
        "price": 1.49,
        "ingredients_text": "Milk, sugar, strawberries, natural flavor",
        "status": 1,
    },
]

# Base URL for OpenFoodFacts API
OPENFOODFACTS_BASE = "https://world.openfoodfacts.org"


def get_all_inventory() -> List[Dict]:
    """Return the full inventory list (read-only view)."""
    return inventory_data


def get_inventory_item(item_id: int) -> Optional[Dict]:
    """Return a single inventory item by `id`, or None if not found."""
    return next((item for item in inventory_data if item["id"] == item_id), None)


def _next_id() -> int:
    """Compute the next integer ID for a new inventory item."""
    return max((item["id"] for item in inventory_data), default=0) + 1


def fetch_openfoodfacts_product(barcode: Optional[str] = None, product_name: Optional[str] = None) -> Optional[Dict]:
    """Query OpenFoodFacts by barcode or product name and return the first matching product.

    - If `barcode` is provided, the product endpoint is used.
    - If `product_name` is provided, a search is performed.
    Returns the product dict on success, or None on failure/no match.
    """
    try:
        if barcode:
            # Barcode lookup (single product endpoint)
            response = requests.get(f"{OPENFOODFACTS_BASE}/api/v0/product/{barcode}.json", timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 1:
                return data.get("product")
            return None

        if product_name:
            # Search endpoint (returns list of products)
            payload = {
                "search_terms": product_name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1,
            }
            response = requests.get(f"{OPENFOODFACTS_BASE}/cgi/search.pl", params=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            return products[0] if products else None
    except (requests.RequestException, ValueError):
        # Network or parsing error — return None so callers can handle gracefully
        return None

    return None


def enhance_item_with_product(item: Dict, product_data: Dict) -> Dict:
    """Update the local `item` dict with fields extracted from `product_data`.

    This merges useful OpenFoodFacts fields while preserving existing values.
    """
    item.update({
        "product_name": product_data.get("product_name", item.get("product_name")),
        "brand": item.get("brand") or product_data.get("brands"),
        "ingredients_text": item.get("ingredients_text") or product_data.get("ingredients_text"),
        "barcode": item.get("barcode") or product_data.get("code"),
        "status": product_data.get("status", item.get("status", 1)),
    })
    return item


def add_inventory_item(payload: Dict) -> Dict:
    """Create and append a new inventory item.

    `payload` may include `product_name`, `brand`, `quantity`, `price`, and `barcode`.
    When possible, the new item is enriched with data fetched from OpenFoodFacts.
    """
    item = {
        "id": _next_id(),
        "product_name": payload.get("product_name", "Unnamed Product"),
        "brand": payload.get("brand", "Unknown"),
        "quantity": int(payload.get("quantity", 0)),
        "price": float(payload.get("price", 0.0)),
        "ingredients_text": payload.get("ingredients_text", ""),
        "barcode": payload.get("barcode"),
        "status": 1,
    }

    # Try to enrich with OpenFoodFacts when barcode or name is provided
    if payload.get("barcode") or payload.get("product_name"):
        product_data = fetch_openfoodfacts_product(barcode=payload.get("barcode"), product_name=payload.get("product_name"))
        if product_data:
            enhance_item_with_product(item, product_data)

    inventory_data.append(item)
    return item


def update_inventory_item(item_id: int, updates: Dict) -> Optional[Dict]:
    """Apply partial updates to an existing inventory item.

    Allowed updates: `quantity`, `price`, `product_name`, `brand`, `ingredients_text`, `barcode`.
    Returns the updated item or None if not found.
    """
    item = get_inventory_item(item_id)
    if not item:
        return None

    if "quantity" in updates:
        item["quantity"] = int(updates["quantity"])
    if "price" in updates:
        item["price"] = float(updates["price"])
    if "product_name" in updates:
        item["product_name"] = updates["product_name"]
    if "brand" in updates:
        item["brand"] = updates["brand"]
    if "ingredients_text" in updates:
        item["ingredients_text"] = updates["ingredients_text"]
    if "barcode" in updates:
        item["barcode"] = updates["barcode"]
    return item


def delete_inventory_item(item_id: int) -> bool:
    """Remove an item from inventory by `id`. Returns True when deleted."""
    item = get_inventory_item(item_id)
    if not item:
        return False
    inventory_data.remove(item)
    return True
