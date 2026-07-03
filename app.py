"""
app.py

Flask HTTP API for the inventory system. Exposes RESTful endpoints that
operate on the in-memory inventory provided by `inventory.py`.
"""

from flask import Flask, jsonify, request
from inventory import (
    add_inventory_item,
    delete_inventory_item,
    fetch_openfoodfacts_product,
    get_all_inventory,
    get_inventory_item,
    update_inventory_item,
)

# Create Flask application
app = Flask(__name__)



# Inventory endpoints

@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Return a JSON list of all inventory items."""
    # Wrap the list in an object so the response can grow with extra metadata later.
    return jsonify({"inventory": get_all_inventory()}), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory(item_id: int):
    """Return a single inventory item by ID or 404 if missing."""
    # Look up the item in the in-memory inventory store.
    item = get_inventory_item(item_id)
    if not item:
        # Return a client-friendly JSON error when the ID does not exist.
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Create an inventory item from JSON payload. Requires `product_name` or `barcode`.

    The newly created item is attempted to be enriched from OpenFoodFacts.
    """
    # Parse JSON safely; invalid or missing JSON becomes None instead of raising.
    payload = request.get_json(force=True, silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    # A product name or barcode is required so the item can be identified.
    if "product_name" not in payload and "barcode" not in payload:
        return jsonify({"error": "product_name or barcode is required"}), 400

    # Delegate item creation and possible OpenFoodFacts enrichment to inventory.py.
    item = add_inventory_item(payload)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def patch_inventory(item_id: int):
    """Apply partial updates to an inventory item."""
    # Accept partial JSON objects such as {"price": 5.25}.
    payload = request.get_json(force=True, silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    # The inventory layer returns None when the item is not found.
    item = update_inventory_item(item_id, payload)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def remove_inventory(item_id: int):
    """Delete an inventory item by ID."""
    # Convert the inventory layer's boolean result into an HTTP response.
    success = delete_inventory_item(item_id)
    if not success:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"message": "Item deleted"}), 200


@app.route("/inventory/search", methods=["GET"])
def search_inventory_api():
    """Proxy to OpenFoodFacts search endpoints.

    Accepts query parameters: `barcode` or `name` and returns the raw product
    JSON returned by OpenFoodFacts.
    """
    # Support either exact barcode lookup or name-based product search.
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if not barcode and not name:
        return jsonify({"error": "barcode or name query parameter is required"}), 400

    # Return the external product JSON directly when a product is found.
    product = fetch_openfoodfacts_product(barcode=barcode, product_name=name)
    if not product:
        return jsonify({"error": "Product not found or API error"}), 404
    return jsonify(product), 200



# Error handlers

@app.errorhandler(404)
def not_found(error):
    # Keep framework-level 404 responses in the same JSON style as API errors.
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    # Hide internal details from API clients while still returning JSON.
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Run the development server when this file is executed directly.
    app.run(debug=True)
