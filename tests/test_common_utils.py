# tests/test_common_utils.py
from unittest.mock import patch
import pytest
from utils import logout, add_logout_button

# Fixture to mock Streamlit
@pytest.fixture
def mock_streamlit():
    with patch("utils.st") as mock_st:
        mock_st.session_state = {}
        yield mock_st

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    return supabase

# Tests for logout
def test_logout_with_supabase(mock_streamlit, mock_supabase):
    mock_streamlit.session_state = {"supabase": mock_supabase}
    with patch("utils.time.sleep") as mock_sleep, patch("utils.switch_page") as mock_switch_page:
        logout()
        mock_supabase.auth.sign_out.assert_called_once()
        assert mock_streamlit.session_state == {}
        mock_streamlit.success.assert_called_once_with("Logged out successfully! ")
        mock_sleep.assert_called_once_with(2)
        mock_switch_page.assert_called_once_with("main")

def test_logout_without_supabase(mock_streamlit):
    mock_streamlit.session_state = {}
    with patch("utils.time.sleep") as mock_sleep, patch("utils.switch_page") as mock_switch_page:
        logout()
        assert mock_streamlit.session_state == {}
        mock_streamlit.success.assert_called_once_with("Logged out successfully! ")
        mock_sleep.assert_called_once_with(2)
        mock_switch_page.assert_called_once_with("main")

# Tests for add_logout_button
def test_add_logout_button(mock_streamlit):
    with patch("utils.logout") as mock_logout:
        add_logout_button()
        mock_streamlit.sidebar.__enter__.assert_called_once()
        mock_streamlit.button.assert_called_once_with("Logout", on_click=mock_logout)