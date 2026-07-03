# Inventory System Summative

A simple inventory management system built with Flask, Python, and a terminal-based CLI. The app stores inventory in memory, exposes REST API endpoints, and can search product details from OpenFoodFacts by barcode or product name.

## Features

- Flask REST API for inventory CRUD operations
- Interactive command-line interface
- In-memory inventory storage using a Python list
- OpenFoodFacts product lookup by barcode or product name
- Unit tests for API routes, inventory helpers, and CLI behavior

## Project Structure

```text
.
├── app.py                    # Flask API routes
├── cli.py                    # Interactive terminal menu
├── inventory.py              # Inventory data and helper functions
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
└── tests/
    ├── test_cli.py           # CLI tests
    └── test_inventory_api.py # API and inventory tests
```

## Requirements

- Python 3
- `pip`
- Internet access for OpenFoodFacts searches and package installation

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API Server

Start the Flask server:

```bash
python app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

## Run the CLI

In a second terminal, activate the same virtual environment and start the CLI:

```bash
source .venv/bin/activate
python cli.py
```

The CLI displays an interactive menu:

```text
1. View all items
2. View a specific item
3. Add a new item
4. Update an item
5. Delete an item
6. Find product (OpenFoodFacts)
7. Exit
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/inventory` | Get all inventory items |
| `GET` | `/inventory/<item_id>` | Get one inventory item by ID |
| `POST` | `/inventory` | Create a new inventory item |
| `PATCH` | `/inventory/<item_id>` | Update an existing inventory item |
| `DELETE` | `/inventory/<item_id>` | Delete an inventory item |
| `GET` | `/inventory/search?barcode=<barcode>` | Search OpenFoodFacts by barcode |
| `GET` | `/inventory/search?name=<name>` | Search OpenFoodFacts by product name |

## Example Requests

Create an inventory item:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Organic Almond Milk",
    "brand": "Silk",
    "quantity": 10,
    "price": 3.99,
    "barcode": "0038000363238"
  }'
```

Update an inventory item:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 15,
    "price": 4.25
  }'
```

Search OpenFoodFacts:

```bash
curl "http://127.0.0.1:5000/inventory/search?barcode=0038000363238"
```

## Testing

Run the test suite:

```bash
pytest
```

If you are using the virtual environment directly:

```bash
.venv/bin/pytest
```

## Notes

- Inventory data is stored in memory, so changes reset when the app restarts.
- The OpenFoodFacts lookup requires internet access.
- The CLI expects the Flask server to already be running at `http://127.0.0.1:5000`.
