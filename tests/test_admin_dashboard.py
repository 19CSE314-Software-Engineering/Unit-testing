# tests/test_admin_dashboard.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import create_employee, process_employee_data, create_department, fetch_all_complaints, filter_complaints_by_status

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.auth.sign_up.return_value = MagicMock(user=MagicMock())
    supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for create_employee
def test_create_employee_success(mock_supabase):
    mock_supabase.auth.sign_up.return_value = MagicMock(user=MagicMock())
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    
    success, message = create_employee(mock_supabase, "John Doe", "john@example.com", "1990-01-01", "555-1234", "Male", 1, 1)
    assert success == True
    assert message == "Employee created successfully!"
    mock_supabase.auth.sign_up.assert_called_once_with({"email": "john@example.com", "password": "abcdef"})

def test_create_employee_missing_input():
    mock_supabase = MagicMock()
    success, message = create_employee(mock_supabase, "", "john@example.com", "1990-01-01", "555-1234", "Male", 1, 1)
    assert success == False
    assert message == "Name and email are required."
    mock_supabase.auth.sign_up.assert_not_called()

# Tests for process_employee_data
def test_process_employee_data():
    employees = [
        {"id": 1, "name": "John", "department": {"dept_name": "IT"}, "positions": {"position_name": "Manager"}},
        {"id": 2, "name": "Jane", "department": None, "positions": None}
    ]
    processed = process_employee_data(employees)
    assert processed[0]["department"] == "IT"
    assert processed[0]["positions"] == "Manager"
    assert processed[1]["department"] is None
    assert processed[1]["positions"] is None

# Tests for create_department
def test_create_department_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    success, message = create_department(mock_supabase, "IT")
    assert success == True
    assert message == "Department added successfully!"
    mock_supabase.table.assert_called_once_with("department")

def test_create_department_empty_name():
    mock_supabase = MagicMock()
    success, message = create_department(mock_supabase, "")
    assert success == False
    assert message == "Enter a department name."
    mock_supabase.table.assert_not_called()

# Tests for fetch_all_complaints
def test_fetch_all_complaints_found(mock_supabase):
    mock_data = [{"id": 1, "category": "waste", "status": "Pending"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_all_complaints(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("customer_complaints")

# Tests for filter_complaints_by_status
def test_filter_complaints_by_status():
    complaints = [
        {"id": 1, "status": "Pending"},
        {"id": 2, "status": "Resolved"}
    ]
    filtered = filter_complaints_by_status(complaints, "Pending")
    assert len(filtered) == 1
    assert filtered[0]["status"] == "Pending"

def test_filter_complaints_by_status_all():
    complaints = [
        {"id": 1, "status": "Pending"},
        {"id": 2, "status": "Resolved"}
    ]
    filtered = filter_complaints_by_status(complaints, "All")
    assert filtered == complaints