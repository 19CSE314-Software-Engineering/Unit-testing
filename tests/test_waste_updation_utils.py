# tests/test_waste_updation.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_assigned_waste_facility_update, update_waste_facility_level

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_assigned_waste_facility_update
def test_fetch_assigned_waste_facility_update_found(mock_supabase):
    mock_data = [
        {
            "facility_id": 1,
            "state_name": "California",
            "status": "Active",
            "description": "Main landfill",
            "last_updated": "2023-01-01",
            "capacity": 1000,
            "waste_level": 50
        }
    ]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_assigned_waste_facility_update(mock_supabase, employee_id=1)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("in_charge_id", 1)

def test_fetch_assigned_waste_facility_update_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_assigned_waste_facility_update(mock_supabase, employee_id=1)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")

# Tests for update_waste_facility_level
def test_update_waste_facility_level_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"facility_id": 1}])
    result, message = update_waste_facility_level(
        supabase=mock_supabase,
        facility_id=1,
        waste_level="50",
        last_updated="2023-01-01"
    )
    assert result == True
    assert message == "Waste level updated successfully!"
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.update.assert_called_once_with({"waste_level": "50", "last_updated": "2023-01-01"})
    mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with("facility_id", 1)

def test_update_waste_facility_level_db_failure(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=None)
    result, message = update_waste_facility_level(
        supabase=mock_supabase,
        facility_id=1,
        waste_level="50",
        last_updated="2023-01-01"
    )
    assert result == False
    assert message == "Failed to update waste level."