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



# Inventory Endpoints

@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Return a JSON list of all inventory items."""
    return jsonify({"inventory": get_all_inventory()}), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory(item_id: int):
    """Return a single inventory item by ID or 404 if missing."""
    item = get_inventory_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Create an inventory item from JSON payload. Requires `product_name` or `barcode`.

    The newly created item is attempted to be enriched from OpenFoodFacts.
    """
    payload = request.get_json(force=True, silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    if "product_name" not in payload and "barcode" not in payload:
        return jsonify({"error": "product_name or barcode is required"}), 400

    item = add_inventory_item(payload)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def patch_inventory(item_id: int):
    """Apply partial updates to an inventory item."""
    payload = request.get_json(force=True, silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    item = update_inventory_item(item_id, payload)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def remove_inventory(item_id: int):
    """Delete an inventory item by ID."""
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
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if not barcode and not name:
        return jsonify({"error": "barcode or name query parameter is required"}), 400

    product = fetch_openfoodfacts_product(barcode=barcode, product_name=name)
    if not product:
        return jsonify({"error": "Product not found or API error"}), 404
    return jsonify(product), 200



# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
