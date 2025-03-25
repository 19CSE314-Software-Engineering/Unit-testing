# tests/test_electricity_admin.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_electricity_employees, fetch_substation_locations, assign_employee_to_substation, fetch_electricity_complaints, update_electricity_complaint

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_electricity_employees
def test_fetch_electricity_employees_found(mock_supabase):
    mock_data = [{"id": 1, "name": "John Doe"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_electricity_employees(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("employees")

# Tests for fetch_substation_locations
def test_fetch_substation_locations_found(mock_supabase):
    mock_data = [{"substation_id": 1, "state_name": "California"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_substation_locations(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("electricity_substations")

# Tests for assign_employee_to_substation
def test_assign_employee_to_substation_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"substation_id": 1}])
    success, message = assign_employee_to_substation(mock_supabase, employee_id=1, substation_id=1)
    assert success == True
    assert message == "Employee assigned successfully!"
    mock_supabase.table.assert_called_once_with("electricity_substations")

# Tests for fetch_electricity_complaints
def test_fetch_electricity_complaints_found(mock_supabase):
    mock_data = [{"id": 1, "category": "Electricity", "status": "Pending"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_electricity_complaints(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("customer_complaints")

# Tests for update_electricity_complaint
def test_update_electricity_complaint_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    success, message = update_electricity_complaint(mock_supabase, complaint_id=1, status="In Progress", employee_id=1)
    assert success == True
    assert message == "Complaint updated successfully!"
    mock_supabase.table.assert_called_once_with("customer_complaints")

def test_update_electricity_complaint_invalid_status():
    mock_supabase = MagicMock()
    success, message = update_electricity_complaint(mock_supabase, complaint_id=1, status="Invalid", employee_id=1)
    assert success == False
    assert message == "Invalid status."
    mock_supabase.table.assert_not_called()