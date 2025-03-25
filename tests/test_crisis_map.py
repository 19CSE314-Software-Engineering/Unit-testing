# tests/test_crisis_map.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_crisis_map_data, fetch_facility_data, fetch_recent_news_updates, filter_crises_by_location, count_crises_by_type

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_crisis_map_data
def test_fetch_crisis_map_data_found(mock_supabase):
    mock_data = [{"crisis_id": 1, "name": "Wildfire", "state_name": "California"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_crisis_map_data(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("crisis_reports")

# Tests for fetch_facility_data
def test_fetch_facility_data_found(mock_supabase):
    mock_data = [{"facility_name": "Shelter", "latitude": 34.0, "longitude": -118.0}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_facility_data(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("facilities")

# Tests for fetch_recent_news_updates
def test_fetch_recent_news_updates_found(mock_supabase):
    mock_data = [{"id": 1, "title": "News Title"}]
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_recent_news_updates(mock_supabase, limit=10)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("crisis_newsboard")

# Tests for filter_crises_by_location
def test_filter_crises_by_location_match():
    crisis_data = [
        {"crisis_id": 1, "state_name": "California", "name": "Wildfire"},
        {"crisis_id": 2, "state_name": "Texas", "name": "Flood"}
    ]
    filtered = filter_crises_by_location(crisis_data, "california")
    assert len(filtered) == 1
    assert filtered[0]["state_name"] == "California"

def test_filter_crises_by_location_empty_query():
    crisis_data = [
        {"crisis_id": 1, "state_name": "California", "name": "Wildfire"},
        {"crisis_id": 2, "state_name": "Texas", "name": "Flood"}
    ]
    filtered = filter_crises_by_location(crisis_data, "")
    assert filtered == crisis_data

# Tests for count_crises_by_type
def test_count_crises_by_type():
    crisis_data = [
        {"crisis_type": "Fire"},
        {"crisis_type": "Flood"},
        {"crisis_type": "Earthquake"},
        {"crisis_type": "Power Outage"},
        {"crisis_type": "Other"}
    ]
    counts = count_crises_by_type(crisis_data)
    assert counts == {
        "Fire": 1,
        "Flood": 1,
        "Earthquake": 1,
        "Power Outage": 1,
        "Other": 1
    }

def test_count_crises_by_type_unknown_type():
    crisis_data = [
        {"crisis_type": "Fire"},
        {"crisis_type": "Unknown"}  # Should raise KeyError
    ]
    with pytest.raises(KeyError, match="Unknown"):
        count_crises_by_type(crisis_data)