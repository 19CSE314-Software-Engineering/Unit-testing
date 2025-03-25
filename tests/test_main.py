# tests/test_main.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import login_user

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.auth.sign_in_with_password.return_value = MagicMock(user=None)
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for login_user
def test_login_user_success(mock_supabase):
    mock_user = MagicMock()
    mock_user.__dict__ = {"id": "user1", "email": "test@example.com"}
    mock_supabase.auth.sign_in_with_password.return_value = MagicMock(user=mock_user)
    mock_employee_data = [{"id": 1, "name": "John Doe", "dept_id": 1, "position_id": 1}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_employee_data)
    
    success, message, employee_data = login_user(mock_supabase, "test@example.com", "password")
    assert success == True
    assert message == "Login successful!"
    assert employee_data == mock_employee_data[0]
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({"email": "test@example.com", "password": "password"})
    mock_supabase.table.assert_called_once_with("employees")
    mock_supabase.table.return_value.select.assert_called_once_with("id, name, dept_id, position_id")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("email", "test@example.com")

def test_login_user_invalid_credentials(mock_supabase):
    mock_supabase.auth.sign_in_with_password.return_value = MagicMock(user=None)
    success, message, employee_data = login_user(mock_supabase, "test@example.com", "wrong_password")
    assert success == False
    assert message == "Invalid credentials."
    assert employee_data == {}
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({"email": "test@example.com", "password": "wrong_password"})

def test_login_user_not_in_employees(mock_supabase):
    mock_user = MagicMock()
    mock_user.__dict__ = {"id": "user1", "email": "test@example.com"}
    mock_supabase.auth.sign_in_with_password.return_value = MagicMock(user=mock_user)
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    
    success, message, employee_data = login_user(mock_supabase, "test@example.com", "password")
    assert success == False
    assert message == "User not found in employees table."
    assert employee_data == {}
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({"email": "test@example.com", "password": "password"})
    mock_supabase.table.assert_called_once_with("employees")
    mock_supabase.table.return_value.select.assert_called_once_with("id, name, dept_id, position_id")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("email", "test@example.com")