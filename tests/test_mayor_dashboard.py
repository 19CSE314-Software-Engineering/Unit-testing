# tests/test_mayor_dashboard.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_all_complaints, filter_complaints_by_status

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_all_complaints (already tested in test_admin_dashboard.py, but included for completeness)
def test_fetch_all_complaints_found(mock_supabase):
    mock_data = [{"id": 1, "category": "waste", "status": "Pending"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_all_complaints(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("customer_complaints")

# Tests for filter_complaints_by_status (already tested in test_admin_dashboard.py, but included for completeness)
def test_filter_complaints_by_status():
    complaints = [
        {"id": 1, "status": "Pending"},
        {"id": 2, "status": "Resolved"}
    ]
    filtered = filter_complaints_by_status(complaints, "Pending")
    assert len(filtered) == 1
    assert filtered[0]["status"] == "Pending"