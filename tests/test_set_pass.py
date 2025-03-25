# tests/test_set_pass.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import set_user_password

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.auth.admin.list_users.return_value = MagicMock(users=[])
    return supabase

# Tests for set_user_password
def test_set_user_password_success(mock_supabase):
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.id = "user1"
    mock_supabase.auth.admin.list_users.return_value = MagicMock(users=[mock_user])
    mock_supabase.auth.admin.update_user_by_id.return_value = None
    
    success, message = set_user_password(mock_supabase, "test@example.com", "new_password")
    assert success == True
    assert message == "Password set successfully! You can now log in."
    mock_supabase.auth.admin.update_user_by_id.assert_called_once_with("user1", {"password": "new_password"})

def test_set_user_password_user_not_found(mock_supabase):
    mock_supabase.auth.admin.list_users.return_value = MagicMock(users=[])
    success, message = set_user_password(mock_supabase, "test@example.com", "new_password")
    assert success == False
    assert message == "User not found! Please check the email."
    mock_supabase.auth.admin.update_user_by_id.assert_not_called()

def test_set_user_password_empty_input():
    mock_supabase = MagicMock()
    success, message = set_user_password(mock_supabase, "", "new_password")
    assert success == False
    assert message == "Both email and password are required!"
    mock_supabase.auth.admin.list_users.assert_not_called()