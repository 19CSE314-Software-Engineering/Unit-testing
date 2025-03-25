# tests/test_citizen_dashboard.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import submit_complaint, fetch_complaints_by_email, fetch_notifications, fetch_welfare_schemes, check_eligibility, apply_for_scheme

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.order.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for submit_complaint
def test_submit_complaint_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    success, message = submit_complaint(mock_supabase, "test@example.com", "John", "555-1234", "waste", "Overflowing bin")
    assert success == True
    assert message == "Complaint submitted successfully!"
    mock_supabase.table.assert_called_once_with("customer_complaints")

def test_submit_complaint_missing_input():
    mock_supabase = MagicMock()
    success, message = submit_complaint(mock_supabase, "", "John", "555-1234", "waste", "Overflowing bin")
    assert success == False
    assert message == "Email, name, and description are required."
    mock_supabase.table.assert_not_called()

# Tests for fetch_complaints_by_email
def test_fetch_complaints_by_email_found(mock_supabase):
    mock_data = [{"category": "waste", "status": "Pending"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_complaints_by_email(mock_supabase, "test@example.com")
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("customer_complaints")

# Tests for fetch_notifications
def test_fetch_notifications_found(mock_supabase):
    mock_data = [{"notification": "Alert", "created_at": "2023-01-01"}]
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_notifications(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("notifications")

# Tests for fetch_welfare_schemes
def test_fetch_welfare_schemes_found(mock_supabase):
    mock_data = [{"id": 1, "name": "Scheme 1", "eligibility_criteria": "age 30"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_welfare_schemes(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("welfare_schemes")

# Tests for check_eligibility
def test_check_eligibility_age_match():
    scheme = {"eligibility_criteria": "age 30"}
    eligible = check_eligibility(scheme, age=30, income=50000, employment_status="Employed")
    assert eligible == True

def test_check_eligibility_no_match():
    scheme = {"eligibility_criteria": "age 30"}
    eligible = check_eligibility(scheme, age=25, income=50000, employment_status="Employed")
    assert eligible == False

# Tests for apply_for_scheme
def test_apply_for_scheme_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    success, message = apply_for_scheme(mock_supabase, "John", 30, 50000, "Employed", "Flood", 1)
    assert success == True
    assert message == "Application submitted successfully!"
    mock_supabase.table.assert_called_once_with("citizen_applications")

def test_apply_for_scheme_missing_name():
    mock_supabase = MagicMock()
    success, message = apply_for_scheme(mock_supabase, "", 30, 50000, "Employed", "Flood", 1)
    assert success == False
    assert message == "Name is required."
    mock_supabase.table.assert_not_called()