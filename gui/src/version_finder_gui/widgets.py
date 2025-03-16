"""Custom widgets used in the GUI application."""

from typing import List
import customtkinter as ctk
from tkinter import messagebox
import logging
import tkinter
from version_finder.version_finder import (
    Commit,
)

logger = logging.getLogger(__name__)


def center_window(window: ctk.CTkToplevel):
    """Center the window on the screen"""
    window.update()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


class CommitListWindow(ctk.CTkToplevel):
    def __init__(self, parent, title: str, commits: List[Commit]):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")

        center_window(self)
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create headers
        header_frame = ctk.CTkFrame(self.scroll_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(header_frame, text="Commit Hash", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Subject", width=500).pack(side="left", padx=5)

        # Add commits
        for commit in commits:
            self._add_commit_row(commit)

    def _create_styled_button(self, parent, text, width=None, command=None):
        return ctk.CTkButton(
            parent,
            text=text,
            width=width,  # Can be None or 0 for expandable buttons
            command=command,
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray30"),
            hover_color=("gray90", "gray20"),
            text_color=("gray10", "gray90"),
            anchor="w"
        )

    def _add_commit_row(self, commit: Commit):
        row = ctk.CTkFrame(self.scroll_frame)
        row.pack(fill="x", pady=2)

        # Configure the row to expand the second column (subject)
        row.grid_columnconfigure(1, weight=1)

        # Hash button (fixed width)
        hash_btn = self._create_styled_button(
            row,
            text=commit.sha[:8],
            width=100,
            command=lambda: self._copy_to_clipboard(commit.sha)
        )
        hash_btn.grid(row=0, column=0, padx=5)  # Changed from pack to grid

        # Subject button (expandable)
        subject_btn = self._create_styled_button(
            row,
            text=commit.subject,
            width=0,  # Set width to 0 to allow expansion
            command=lambda: self._toggle_commit_details_card(subject_btn, commit)
        )
        subject_btn.grid(row=0, column=1, padx=5, sticky="ew")  # sticky="ew" makes it expand horizontally

    def _toggle_commit_details_card(self, button: ctk.CTkButton, commit: Commit):
        # Check if the card already exists
        if hasattr(self, "card") and self.card.winfo_exists():
            self.card.destroy()  # Close the card if it's already open
            return

        # Get the button's position
        x = button.winfo_rootx() - self.winfo_rootx()
        y = button.winfo_rooty() - self.winfo_rooty() + button.winfo_height()
        button_width = button.winfo_width()

        # Check if the card would be cut off
        card_height = 200  # Default height for the card before content calculation
        app_height = self.winfo_height()

        if y + card_height > app_height:  # If the card would be cut off
            y = button.winfo_rooty() - self.winfo_rooty() - card_height

        # Create the card
        self.card = ctk.CTkFrame(self, corner_radius=15, fg_color="white", width=button_width)
        self.card.place(x=x, y=y)  # Place it on top of the button

        # Split message into first line and rest
        message_lines = (commit.message or "").split('\n', 1)
        first_line = message_lines[0]
        rest_of_message = message_lines[1] if len(message_lines) > 1 else ""

        # Add first line in bold
        first_line_label = ctk.CTkLabel(self.card, text=first_line, font=("Arial", 14, "bold"))
        first_line_label.pack(pady=5, padx=10, anchor="w")

        # Add rest of message if it exists
        if rest_of_message:
            message_label = ctk.CTkLabel(
                self.card, text=rest_of_message, font=(
                    "Arial", 12), wraplength=button_width - 20)
            message_label.pack(pady=5, padx=10, anchor="w")

        # Author with label
        author_label = ctk.CTkLabel(self.card, text=f"Author: {commit.author}", font=("Arial", 12))
        author_label.pack(pady=5, padx=10, anchor="w")

        # Convert timestamp to human readable format
        from datetime import datetime
        try:
            timestamp_dt = datetime.fromtimestamp(float(commit.timestamp))
            formatted_time = timestamp_dt.strftime("%B %d, %Y at %I:%M %p")
            timestamp_label = ctk.CTkLabel(self.card, text=formatted_time, font=("Arial", 12))
            timestamp_label.pack(pady=5, padx=10, anchor="w")
        except (ValueError, TypeError):
            # Fallback in case timestamp conversion fails
            timestamp_label = ctk.CTkLabel(self.card, text=str(commit.timestamp), font=("Arial", 12))
            timestamp_label.pack(pady=5, padx=10, anchor="w")

        # Version with label (if exists)
        if commit.version:
            version_label = ctk.CTkLabel(self.card, text=f"Version: {commit.version}", font=("Arial", 12))
            version_label.pack(pady=5, padx=10, anchor="w")

        close_button = ctk.CTkButton(self.card, text="Close", command=self.card.destroy)
        close_button.pack(pady=5)

        # Update the card height dynamically based on content
        self.card.update_idletasks()
        card_height = self.card.winfo_reqheight()
        self.card.configure(height=card_height)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commit hash copied to clipboard!")


class AutocompleteEntry(ctk.CTkEntry):
    """A customtkinter entry widget with autocomplete functionality."""

    def __init__(self, *args, placeholder_text: str = '', callback: callable = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._suggestions: list[str] = []
        self._placeholder_text: str = placeholder_text
        self._placeholder_shown: bool = True
        self.callback: callable | None = callback
        self.suggestion_window: ctk.CTkToplevel | None = None
        self._text_color = "black"
        self._temp_selection: str = ''

        # Bind events
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<FocusIn>', self._on_focus_in)

        # Show initial placeholder
        self._show_placeholder()

    @property
    def suggestions(self) -> list[str]:
        return self._suggestions

    @suggestions.setter
    def suggestions(self, value: list[str] | None) -> None:
        self._suggestions = value if value is not None else []

    @property
    def placeholder_text(self) -> str:
        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value: str) -> None:
        self._placeholder_text = value

    def _show_placeholder(self) -> None:
        super().delete(0, "end")
        if self.placeholder_text:
            super().insert(0, self._placeholder_text)
        self.configure(text_color='gray')
        self._placeholder_shown = True

    def get(self) -> str:
        if self._placeholder_shown or self.cget("state") == "disabled":
            return ''
        return super().get()

    def insert(self, index: str, string: str) -> None:
        if self._placeholder_shown:
            super().delete(0, "end")
            self.configure(text_color=self._text_color)
            self._placeholder_shown = False
        super().insert(index, string)

    def _get_filtered_suggestions(self) -> list[str]:
        text = self.get().lower()
        exact_matches = [s for s in self._suggestions if s.lower().startswith(text)]
        contains_matches = [s for s in self._suggestions if text in s.lower() and not s.lower().startswith(text)]
        return sorted(exact_matches) + sorted(contains_matches)

    def _show_suggestions(self) -> None:
        suggestions = self._get_filtered_suggestions()
        if not suggestions:
            if self.suggestion_window:
                self.suggestion_window.destroy()
                self.suggestion_window = None
            return

        if self.suggestion_window:
            self.suggestion_window.destroy()

        self.suggestion_window = ctk.CTkToplevel()
        self.suggestion_window.withdraw()
        self.suggestion_window.overrideredirect(True)

        suggestion_frame = ctk.CTkScrollableFrame(self.suggestion_window)
        suggestion_frame.pack(fill="both", expand=True)

        for suggestion in suggestions:
            btn = ctk.CTkButton(
                suggestion_frame,
                text=suggestion,
                command=lambda s=suggestion: self._select_suggestion(s)
            )
            btn.pack(fill="x", padx=2, pady=1)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.suggestion_window.geometry(f"{self.winfo_width()}x200+{x}+{y}")
        self.suggestion_window.deiconify()

    def _select_suggestion(self, suggestion: str) -> None:
        self.delete(0, "end")
        self.insert(0, suggestion)
        self._temp_selection = suggestion  # Set the current selection so previous text is not reinserted
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        # Move focus to parent window
        self.master.focus_set()
        if self.callback:
            self.callback(suggestion)

    def _on_key_release(self, event: 'tkinter.Event') -> str | None:
        self._show_suggestions()

    def _on_focus_out(self, event: 'tkinter.Event') -> None:
        if self.suggestion_window:
            self.after(100, self._destroy_suggestion_window)

        if self.get() and not self._placeholder_shown:
            self.configure(text_color=self._text_color)
        else:
            self._show_placeholder()

        self._temp_selection = ''

    def _on_focus_in(self, event: 'tkinter.Event') -> str | None:
        self._temp_selection = self.get()
        super().delete(0, "end")
        self.configure(text_color="black")
        self._placeholder_shown = False
        self._show_suggestions()

    def _destroy_suggestion_window(self) -> None:
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None


class LoadingSpinner(ctk.CTkFrame):
    """A loading spinner widget that shows animation during long operations"""

    def __init__(self, master, text="Loading...", size=30, thickness=3, color=None, text_color=None, **kwargs):
        super().__init__(master, **kwargs)

        # Configure the frame
        self.configure(fg_color=("gray90", "gray10"))

        # Set default colors if not provided
        if color is None:
            color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        if text_color is None:
            text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

        # Store parameters
        self.size = size
        self.thickness = thickness
        self.color = color
        self.angle = 0
        self.is_running = False
        self.after_id = None

        # Create canvas for spinner
        self.canvas = ctk.CTkCanvas(
            self,
            width=size,
            height=size,
            bg=self.cget("fg_color")[0 if ctk.get_appearance_mode() == "Light" else 1],
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Create label for text
        self.label = ctk.CTkLabel(
            self,
            text=text,
            text_color=text_color
        )
        self.label.grid(row=0, column=1, padx=10, pady=10)

        # Draw initial spinner
        self._draw_spinner()

    def _draw_spinner(self):
        """Draw the spinner at the current angle"""
        self.canvas.delete("spinner")

        # Calculate coordinates
        x0 = y0 = self.thickness
        x1 = y1 = self.size - self.thickness

        # Draw arc with gradient color
        start_angle = self.angle
        extent = 120  # Arc length in degrees

        # Draw the spinner arc
        self.canvas.create_arc(
            x0, y0, x1, y1,
            start=start_angle,
            extent=extent,
            outline=self.color if isinstance(self.color, str) else self.color[1],
            width=self.thickness,
            style="arc",
            tags="spinner"
        )

    def _update_spinner(self):
        """Update the spinner animation"""
        if not self.is_running:
            return

        # Update angle
        self.angle = (self.angle + 10) % 360
        self._draw_spinner()

        # Schedule next update
        self.after_id = self.after(50, self._update_spinner)

    def start(self):
        """Start the spinner animation"""
        if not self.is_running:
            self.is_running = True
            self.grid()  # Make sure the spinner is visible
            self._update_spinner()

    def stop(self):
        """Stop the spinner animation"""
        self.is_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.grid_remove()  # Hide the spinner
