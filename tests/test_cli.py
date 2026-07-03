import json
import sys
from unittest.mock import patch
import pytest
import cli


class DummyResponse:
    def __init__(self, ok=True, status_code=200, json_data=None, text=""):
        self.ok = ok
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


@patch("cli.requests.get")
def test_cli_view_all(mock_get, capsys):
    mock_get.return_value = DummyResponse(json_data={"inventory": []})
    sys.argv = ["cli.py", "view"]
    cli.main()
    captured = capsys.readouterr()
    assert "inventory" in captured.out


@patch("cli.requests.post")
def test_cli_add_new_item(mock_post, capsys):
    mock_post.return_value = DummyResponse(json_data={"id": 2, "product_name": "New Item"})
    sys.argv = ["cli.py", "add", "--name", "New Item", "--quantity", "5", "--price", "2.5"]
    cli.main()
    captured = capsys.readouterr()
    assert "New Item" in captured.out


@patch("cli.requests.patch")
def test_cli_update_item(mock_patch, capsys):
    mock_patch.return_value = DummyResponse(json_data={"id": 1, "price": 4.99})
    sys.argv = ["cli.py", "update", "--id", "1", "--price", "4.99"]
    cli.main()
    captured = capsys.readouterr()
    assert "4.99" in captured.out


@patch("cli.requests.delete")
def test_cli_delete_item(mock_delete, capsys):
    mock_delete.return_value = DummyResponse(json_data={"message": "Item deleted"})
    sys.argv = ["cli.py", "delete", "--id", "1"]
    cli.main()
    captured = capsys.readouterr()
    assert "Item deleted" in captured.out


@patch("cli.requests.get")
def test_cli_find_item(mock_get, capsys):
    mock_get.return_value = DummyResponse(json_data={"product_name": "Test Product"})
    sys.argv = ["cli.py", "find", "--barcode", "12345"]
    cli.main()
    captured = capsys.readouterr()
    assert "Test Product" in captured.out
