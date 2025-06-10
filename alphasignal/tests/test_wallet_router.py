from fastapi.testclient import TestClient
from alphasignal.app import app
from unittest.mock import patch

client = TestClient(app)


@patch("alphasignal.routers.wallet_router.retrieve_wallet_value")
@patch("alphasignal.routers.wallet_router.load_wallet")
def test_wallet_value_success(mock_load_wallet, mock_retrieve_wallet_value):
    # Mock successful retrieval
    mock_wallet = object()
    mock_load_wallet.return_value = mock_wallet
    mock_retrieve_wallet_value.return_value = {
        "wallet_tokens": [],
        "total_value": 0,
        "percent_change_value_24h": 0,
    }

    response = client.get("/wallet-value")
    assert response.status_code == 200
    json_data = response.json()
    assert "wallet_tokens" in json_data
    assert json_data["wallet_tokens"] == []
    assert json_data["total_value"] == 0
    assert json_data["percent_change_value_24h"] == 0


@patch("alphasignal.routers.wallet_router.retrieve_wallet_value")
@patch("alphasignal.routers.wallet_router.load_wallet")
def test_wallet_value_error(mock_load_wallet, mock_retrieve_wallet_value):
    # Mock retrieval error
    mock_load_wallet.return_value = object()
    mock_retrieve_wallet_value.side_effect = Exception("Test error")

    response = client.get("/wallet-value")
    assert response.status_code == 404
    assert "detail" in response.json()


@patch("alphasignal.routers.wallet_router.retrieve_sol_value")
@patch("alphasignal.routers.wallet_router.load_wallet")
def test_sol_value_success(mock_load_wallet, mock_retrieve_sol_value):
    # Mock successful SOL value retrieval
    mock_wallet = object()
    mock_load_wallet.return_value = mock_wallet
    mock_retrieve_sol_value.return_value = {"usd_balance": 123.45}

    response = client.get("/sol-value")
    assert response.status_code == 200
    json_data = response.json()
    assert "usd_balance" in json_data
    assert json_data["usd_balance"] == 123.45


@patch("alphasignal.routers.wallet_router.retrieve_sol_value")
@patch("alphasignal.routers.wallet_router.load_wallet")
def test_sol_value_error(mock_load_wallet, mock_retrieve_sol_value):
    # Mock SOL value retrieval error
    mock_load_wallet.return_value = object()
    mock_retrieve_sol_value.side_effect = Exception("Test error")

    response = client.get("/sol-value")
    assert response.status_code == 404
    assert "detail" in response.json()
