"""
cli.py

Simple interactive CLI for the inventory API. Uses HTTP requests to the
running Flask server and provides a text menu to perform CRUD operations
and to search the OpenFoodFacts database via the API.
"""

import requests
import json

DEFAULT_SERVER = "http://127.0.0.1:5000"


def print_menu():
    """Print the main menu options."""
    # Display the available actions each time the loop asks for a choice.
    print("\n" + "="*50)
    print("       INVENTORY MANAGEMENT CLI")
    print("="*50)
    print("1. View all items")
    print("2. View a specific item")
    print("3. Add a new item")
    print("4. Update an item")
    print("5. Delete an item")
    print("6. Find product (OpenFoodFacts)")
    print("7. Exit")
    print("="*50)


def view_all():
    """Request and display all inventory items."""
    try:
        # Ask the Flask API for the current inventory list.
        response = requests.get(f"{DEFAULT_SERVER}/inventory")
        if response.status_code == 200:
            data = response.json()
            items = data.get("inventory", [])
            if items:
                print("\n[INVENTORY] All Items:")
                # Print the main fields for each inventory record.
                for item in items:
                    print(f"\n  ID: {item['id']}")
                    print(f"  Name: {item['product_name']}")
                    print(f"  Brand: {item['brand']}")
                    print(f"  Quantity: {item['quantity']}")
                    print(f"  Price: ${item['price']:.2f}")
            else:
                print("\n[ERROR] No items in inventory")
        else:
            print("\n[ERROR] Error fetching inventory")
    except Exception as e:
        # Catch connection errors so the CLI does not crash if the server is down.
        print(f"\n[ERROR] Error: {e}")


def view_item():
    """Request and display a single item by its ID."""
    try:
        # Convert the user's input to an integer before placing it in the URL.
        item_id = int(input("\nEnter item ID: "))
        response = requests.get(f"{DEFAULT_SERVER}/inventory/{item_id}")
        if response.status_code == 200:
            item = response.json()
            # Show detailed fields for the matching inventory item.
            print("\n[ITEM] Item Details:")
            print(f"  ID: {item['id']}")
            print(f"  Name: {item['product_name']}")
            print(f"  Brand: {item['brand']}")
            print(f"  Quantity: {item['quantity']}")
            print(f"  Price: ${item['price']:.2f}")
            print(f"  Ingredients: {item.get('ingredients_text', 'N/A')}")
        else:
            print("\n[ERROR] Item not found")
    except ValueError:
        print("\n[ERROR] Invalid ID")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")


def add_item():
    """Collect input and POST a new item to the API."""
    try:
        # Gather required and optional values from the terminal user.
        name = input("\nProduct name: ")
        brand = input("Brand (default: Unknown): ") or "Unknown"
        quantity = int(input("Quantity: "))
        price = float(input("Price: $"))
        barcode = input("Barcode (optional): ") or None

        # Build the JSON request body expected by the create endpoint.
        payload = {
            "product_name": name,
            "brand": brand,
            "quantity": quantity,
            "price": price,
        }
        if barcode:
            # Include barcode only when the user supplied one.
            payload["barcode"] = barcode

        response = requests.post(f"{DEFAULT_SERVER}/inventory", json=payload)
        if response.status_code == 201:
            item = response.json()
            print(f"\n[SUCCESS] Item added! ID: {item['id']}")
        else:
            print("\n[ERROR] Error adding item")
    except ValueError:
        print("\n[ERROR] Invalid input")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")


def update_item():
    """Collect fields to update and PATCH the item on the API."""
    try:
        # The API needs the item ID to know which record to patch.
        item_id = int(input("\nEnter item ID: "))
        print("Leave blank to skip a field")

        # Only non-blank fields are added to the update payload.
        updates = {}
        name = input("New name (blank to skip): ")
        if name:
            updates["product_name"] = name

        brand = input("New brand (blank to skip): ")
        if brand:
            updates["brand"] = brand

        quantity = input("New quantity (blank to skip): ")
        if quantity:
            updates["quantity"] = int(quantity)

        price = input("New price (blank to skip): ")
        if price:
            updates["price"] = float(price)

        if not updates:
            # Avoid sending an empty PATCH request.
            print("\n[ERROR] No updates provided")
            return

        # Send the partial update to the Flask API.
        response = requests.patch(f"{DEFAULT_SERVER}/inventory/{item_id}", json=updates)
        if response.status_code == 200:
            print("\n[SUCCESS] Item updated!")
        else:
            print("\n[ERROR] Item not found")
    except ValueError:
        print("\n[ERROR] Invalid input")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")


def delete_item():
    """Prompt and DELETE an item by ID."""
    try:
        # Confirm destructive CLI actions before calling the delete endpoint.
        item_id = int(input("\nEnter item ID to delete: "))
        confirm = input(f"Delete item {item_id}? (y/n): ").lower()
        if confirm == 'y':
            response = requests.delete(f"{DEFAULT_SERVER}/inventory/{item_id}")
            if response.status_code == 200:
                print("\n[SUCCESS] Item deleted!")
            else:
                print("\n[ERROR] Item not found")
        else:
            print("\n[INFO] Cancelled")
    except ValueError:
        print("\n[ERROR] Invalid ID")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")


def find_product():
    """Search OpenFoodFacts via the API by barcode or name."""
    try:
        # Let the user choose between exact barcode lookup and name search.
        print("\nSearch OpenFoodFacts:")
        print("1. By barcode")
        print("2. By product name")
        choice = input("Choose (1 or 2): ")

        if choice == '1':
            # Forward barcode searches to the API proxy endpoint.
            barcode = input("Enter barcode: ")
            response = requests.get(f"{DEFAULT_SERVER}/inventory/search", params={"barcode": barcode})
        elif choice == '2':
            # Forward name searches to the same endpoint with a name parameter.
            name = input("Enter product name: ")
            response = requests.get(f"{DEFAULT_SERVER}/inventory/search", params={"name": name})
        else:
            print("\n[ERROR] Invalid choice")
            return

        if response.status_code == 200:
            product = response.json()
            # Display the most useful fields from the OpenFoodFacts product.
            print("\n[SEARCH] Product Found:")
            print(f"  Name: {product.get('product_name', 'N/A')}")
            print(f"  Brand: {product.get('brands', 'N/A')}")
            print(f"  Ingredients: {product.get('ingredients_text', 'N/A')[:100]}...")
        else:
            print("\n[ERROR] Product not found")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")


def main():
    """Main menu loop."""
    while True:
        # Reprint the menu after each action until the user chooses to exit.
        print_menu()
        choice = input("Enter your choice (1-7): ")

        # Route the selected menu option to the matching CLI function.
        if choice == '1':
            view_all()
        elif choice == '2':
            view_item()
        elif choice == '3':
            add_item()
        elif choice == '4':
            update_item()
        elif choice == '5':
            delete_item()
        elif choice == '6':
            find_product()
        elif choice == '7':
            print("\n[EXIT] Goodbye!")
            break
        else:
            print("\n[ERROR] Invalid choice. Try again.")



if __name__ == "__main__":
    # Start the interactive CLI only when this file is executed directly.
    main()
