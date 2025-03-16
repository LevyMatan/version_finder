import pytest
import customtkinter as ctk
from unittest.mock import MagicMock
from version_finder_gui.widgets import AutocompleteEntry


@pytest.fixture(scope="session")
def tk_app():
    try:
        app = ctk.CTk()
    except BaseException:
        # Mock CTk for headless environments
        app = MagicMock()
        app.winfo_exists = MagicMock(return_value=True)
        app.winfo_width = MagicMock(return_value=100)
        app.winfo_height = MagicMock(return_value=100)
        app.winfo_rootx = MagicMock(return_value=0)
        app.winfo_rooty = MagicMock(return_value=0)
    yield app
    if not isinstance(app, MagicMock):
        app.destroy()


@pytest.fixture
def root(tk_app):
    yield tk_app


@pytest.fixture
def entry(root):
    entry = AutocompleteEntry(root, placeholder_text="Test Entry")
    yield entry
    entry.destroy()


def test_initial_state(entry):
    assert entry.get() == ""
    assert entry.suggestions == []
    assert entry.placeholder_text == "Test Entry"


def test_set_suggestions(entry):
    suggestions = ["apple", "banana", "cherry"]
    entry.suggestions = suggestions
    assert entry.suggestions == suggestions


def test_select_suggestion(entry):
    suggestions = ["apple", "banana", "cherry"]
    entry.suggestions = suggestions

    # Simulate selecting a suggestion
    entry._select_suggestion("banana")
    assert entry.get() == "banana"


def test_callback_on_selection(root):
    callback_value = None

    def on_select(value):
        nonlocal callback_value
        callback_value = value

    entry = AutocompleteEntry(root, callback=on_select)
    entry.suggestions = ["apple", "banana", "cherry"]

    # Simulate selecting a suggestion
    entry._select_suggestion("banana")
    assert callback_value == "banana"


def test_disabled_state(entry):
    entry.configure(state="disabled")
    assert entry.cget("state") == "disabled"

    # Should not be able to modify when readonly
    entry.insert(0, "test")
    assert entry.get() == ""


def test_normal_state(entry):
    entry.configure(state="normal")
    assert entry.cget("state") == "normal"

    # Should be able to modify when normal
    entry.insert(0, "test")
    assert entry.get() == "test"


def test_suggestion_filtering(entry):
    entry.suggestions = ["apple", "banana", "cherry"]

    # Test prefix matching
    entry.insert(0, "ba")
    matches = entry._get_filtered_suggestions()
    assert matches == ["banana"]

    # Test contains matching
    entry.delete(0, "end")
    entry.insert(0, "er")
    matches = entry._get_filtered_suggestions()
    assert matches == ["cherry"]


def test_placeholder_behavior(entry):
    assert entry._placeholder_shown
    assert entry.get() == ""  # Should not return placeholder text

    # Regular text should replace placeholder
    entry.insert(0, "test")
    assert not entry._placeholder_shown
    assert entry.get() == "test"

    # Clearing should restore placeholder after focus out
    entry.delete(0, "end")

    # Simulate focus out
    entry._on_focus_out(None)

    assert entry._placeholder_shown
    assert entry.get() == ""
