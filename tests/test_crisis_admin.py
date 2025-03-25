# tests/test_crisis_admin.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_crisis_reports, update_crisis_report, delete_crisis_report, post_news_update, fetch_recent_news_updates

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_crisis_reports
def test_fetch_crisis_reports_found(mock_supabase):
    mock_data = [{"crisis_id": 1, "name": "Wildfire"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_crisis_reports(mock_supabase, employee_id=1)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("crisis_reports")

# Tests for update_crisis_report
def test_update_crisis_report_success(mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"crisis_id": 1}])
    success, message = update_crisis_report(mock_supabase, crisis_id=1, severity=3, description="Updated description")
    assert success == True
    assert message == "Crisis updated successfully!"
    mock_supabase.table.assert_called_once_with("crisis_reports")

def test_update_crisis_report_invalid_severity():
    mock_supabase = MagicMock()
    success, message = update_crisis_report(mock_supabase, crisis_id=1, severity=6, description="Updated description")
    assert success == False
    assert message == "Severity must be between 1 and 5."
    mock_supabase.table.assert_not_called()

# Tests for delete_crisis_report
def test_delete_crisis_report_success(mock_supabase):
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"crisis_id": 1}])
    success, message = delete_crisis_report(mock_supabase, crisis_id=1)
    assert success == True
    assert message == "Crisis resolved and removed."
    mock_supabase.table.assert_called_once_with("crisis_reports")

# Tests for post_news_update
def test_post_news_update_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    success, message = post_news_update(mock_supabase, "News Title", "News Content", crisis_id=1, posted_by="Admin")
    assert success == True
    assert message == "News update posted successfully!"
    mock_supabase.table.assert_called_once_with("crisis_newsboard")

def test_post_news_update_missing_input():
    mock_supabase = MagicMock()
    success, message = post_news_update(mock_supabase, "", "News Content", crisis_id=1, posted_by="Admin")
    assert success == False
    assert message == "Title and content are required."
    mock_supabase.table.assert_not_called()

# Tests for fetch_recent_news_updates
def test_fetch_recent_news_updates_found(mock_supabase):
    mock_data = [{"id": 1, "title": "News Title"}]
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_recent_news_updates(mock_supabase, limit=10)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("crisis_newsboard")