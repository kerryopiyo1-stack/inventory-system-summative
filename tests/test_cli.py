from unittest.mock import patch
import cli


class DummyResponse:
    # Minimal stand-in for requests.Response used by CLI tests.
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        # Return the fake JSON body configured by each test.
        return self._json_data


@patch("cli.requests.get")
def test_view_all(mock_get, capsys):
    # Mock the inventory endpoint response and capture printed CLI output.
    mock_get.return_value = DummyResponse(json_data={"inventory": [{"id": 1, "product_name": "Test Item", "brand": "Test Brand", "quantity": 5, "price": 2.5}]})
    cli.view_all()
    captured = capsys.readouterr()
    assert "Test Item" in captured.out
    assert "Brand" in captured.out


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1"])
def test_view_item(mock_input, mock_get, capsys):
    # Simulate entering an item ID and receiving one inventory record.
    mock_get.return_value = DummyResponse(json_data={"id": 1, "product_name": "Test Item", "brand": "Test Brand", "quantity": 5, "price": 2.5, "ingredients_text": "Sugar"})
    cli.view_item()
    captured = capsys.readouterr()
    assert "Test Item" in captured.out
    assert "Ingredients" in captured.out


@patch("cli.requests.post")
@patch("builtins.input", side_effect=["New Item", "Brand", "10", "3.50", ""])
def test_add_item(mock_input, mock_post, capsys):
    # Simulate successful item creation from CLI input.
    mock_post.return_value = DummyResponse(status_code=201, json_data={"id": 2, "product_name": "New Item"})
    cli.add_item()
    captured = capsys.readouterr()
    assert "Item added" in captured.out


@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["1", "", "", "", "4.99"])
def test_update_item(mock_input, mock_patch, capsys):
    # Only the price input is provided; the other fields are skipped.
    mock_patch.return_value = DummyResponse(status_code=200, json_data={"id": 1, "price": 4.99})
    cli.update_item()
    captured = capsys.readouterr()
    assert "Item updated" in captured.out


@patch("cli.requests.delete")
@patch("builtins.input", side_effect=["1", "y"])
def test_delete_item(mock_input, mock_delete, capsys):
    # Simulate confirming deletion and receiving a success response.
    mock_delete.return_value = DummyResponse(status_code=200, json_data={"message": "Item deleted"})
    cli.delete_item()
    captured = capsys.readouterr()
    assert "Item deleted" in captured.out


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1", "12345"])
def test_find_product_by_barcode(mock_input, mock_get, capsys):
    # Simulate barcode search through the CLI menu.
    mock_get.return_value = DummyResponse(status_code=200, json_data={"product_name": "Test Product", "brands": "Test Brand", "ingredients_text": "Test ingredient"})
    cli.find_product()
    captured = capsys.readouterr()
    assert "Test Product" in captured.out


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["2", "Test Product"])
def test_find_product_by_name(mock_input, mock_get, capsys):
    # Simulate product-name search through the CLI menu.
    mock_get.return_value = DummyResponse(status_code=200, json_data={"product_name": "Test Product", "brands": "Test Brand", "ingredients_text": "Test ingredient"})
    cli.find_product()
    captured = capsys.readouterr()
    assert "Test Product" in captured.out
