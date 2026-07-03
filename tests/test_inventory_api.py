import json
from unittest.mock import patch

import pytest
from app import app
import inventory


@pytest.fixture(autouse=True)
def reset_inventory_data():
    # Reset the global in-memory inventory before every test for isolation.
    inventory.inventory_data = [
        {
            "id": 1,
            "barcode": "0038000363238",
            "product_name": "Organic Almond Milk",
            "brand": "Silk",
            "quantity": 12,
            "price": 3.99,
            "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, natural flavors",
            "status": 1,
        }
    ]
    # Let the test run after the fresh fixture data has been installed.
    yield


def test_list_inventory_returns_all_items():
    # Use Flask's test client so the route can be tested without a live server.
    client = app.test_client()
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert "inventory" in data
    assert len(data["inventory"]) == 1


def test_get_inventory_item_by_id():
    # Confirm that the detail endpoint returns the seeded inventory record.
    client = app.test_client()
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["product_name"] == "Organic Almond Milk"


def test_get_inventory_item_not_found():
    # Unknown IDs should return a 404 response.
    client = app.test_client()
    response = client.get("/inventory/999")
    assert response.status_code == 404


@patch("inventory.fetch_openfoodfacts_product")
def test_create_inventory_adds_item(mock_fetch):
    # Mock OpenFoodFacts so the create route does not depend on the network.
    mock_fetch.return_value = {
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "code": "0038000363238",
        "status": 1,
    }

    # Post a valid item payload and verify the API assigns the next ID.
    client = app.test_client()
    payload = {
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "quantity": 5,
        "price": 4.50,
        "barcode": "0038000363238",
    }
    response = client.post("/inventory", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 2
    assert data["barcode"] == "0038000363238"
    assert data["product_name"] == "Organic Almond Milk"


def test_create_inventory_missing_payload():
    # Empty JSON should fail validation because name or barcode is required.
    client = app.test_client()
    response = client.post("/inventory", data=json.dumps({}), content_type="application/json")
    assert response.status_code == 400


def test_update_inventory_item():
    # Patch only the fields that should change.
    client = app.test_client()
    payload = {"price": 5.25, "quantity": 15}
    response = client.patch("/inventory/1", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 5.25
    assert data["quantity"] == 15


def test_delete_inventory_item():
    # Delete the seeded item, then verify it can no longer be fetched.
    client = app.test_client()
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item deleted"
    response = client.get("/inventory/1")
    assert response.status_code == 404


@patch("inventory.requests.get")
def test_fetch_openfoodfacts_product_by_barcode(mock_get):
    # Mock the requests response object used inside fetch_openfoodfacts_product.
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Test Product",
            "brands": "Test Brand",
            "ingredients_text": "Test ingredient",
            "code": "12345",
            "status": 1,
        },
    }

    # Barcode lookup should return the product object from the API payload.
    product = inventory.fetch_openfoodfacts_product(barcode="12345")
    assert product["product_name"] == "Test Product"


@patch("inventory.requests.get")
def test_fetch_openfoodfacts_product_by_name(mock_get):
    # Mock a search response containing one matching product.
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Test Product",
                "brands": "Test Brand",
                "ingredients_text": "Test ingredient",
                "code": "98765",
                "status": 1,
            }
        ]
    }

    # Name lookup should return the first product from the products list.
    product = inventory.fetch_openfoodfacts_product(product_name="Test Product")
    assert product["code"] == "98765"
