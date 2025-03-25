# tests/test_waste_admin.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_waste_employees, fetch_waste_facilities, fetch_waste_complaints, update_waste_complaint, assign_employee_to_waste_facility

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_waste_employees
def test_fetch_waste_employees_found(mock_supabase):
    mock_data = [{"id": 1, "name": "John Doe"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_waste_employees(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("employees")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("dept_id", 5)

def test_fetch_waste_employees_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_waste_employees(mock_supabase)
    assert data == []
    mock_supabase.table.assert_called_once_with("employees")

# Tests for fetch_waste_facilities
def test_fetch_waste_facilities_found(mock_supabase):
    mock_data = [{"facility_id": 1, "state_name": "California"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_waste_facilities(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.assert_called_once_with("facility_id, state_name")

def test_fetch_waste_facilities_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_waste_facilities(mock_supabase)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")

# Tests for fetch_waste_complaints
def test_fetch_waste_complaints_found(mock_supabase):
    mock_data = [{"id": 1, "category": "waste", "description": "Overflowing bin"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_waste_complaints(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("customer_complaints")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("category", "waste")

def test_fetch_waste_complaints_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_waste_complaints(mock_supabase)
    assert data == []
    mock_supabase.table.assert_called_once_with("customer_complaints")

# Tests for update_waste_complaint
def test_update_waste_complaint_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    result, message = update_waste_complaint(mock_supabase, complaint_id=1, status="In Progress", employee_id=1)
    assert result == True
    assert message == "Complaint updated successfully!"
    mock_supabase.table.assert_called_once_with("customer_complaints")
    mock_supabase.table.return_value.update.assert_called_once_with({"status": "In Progress", "assign": 1})

def test_update_waste_complaint_invalid_status(mock_supabase):
    result, message = update_waste_complaint(mock_supabase, complaint_id=1, status="Invalid", employee_id=1)
    assert result == False
    assert message == "Invalid status."
    mock_supabase.table.assert_not_called()

# Tests for assign_employee_to_waste_facility
def test_assign_employee_to_waste_facility_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"facility_id": 1}])
    result, message = assign_employee_to_waste_facility(mock_supabase, employee_id=1, facility_id=1)
    assert result == True
    assert message == "Employee assigned successfully!"
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.update.assert_called_once_with({"in_charge_id": 1})

def test_assign_employee_to_waste_facility_failure(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=None)
    result, message = assign_employee_to_waste_facility(mock_supabase, employee_id=1, facility_id=1)
    assert result == False
    assert message == "Failed to assign employee."