"""Custom widgets used in the GUI application."""

from typing import Dict, List
import customtkinter as ctk
from tkinter import messagebox
from version_finder.version_finder import (
    Commit,
)


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
    def __init__(self, parent, commits: List[Commit]):
        super().__init__(parent)
        self.title("Commits List")
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
    def __init__(self, *args, placeholder_text='', **kwargs):
        self.suggestions = kwargs.pop('suggestions', [])
        super().__init__(*args, placeholder_text=placeholder_text, **kwargs)

        self._placeholder_text = placeholder_text
        self._placeholder_shown = True
        self.callable = None
        self.suggestion_window = None
        self.suggestion_listbox = None

        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._on_focus_out)

        # Initialize placeholder if provided
        if self._placeholder_text:
            self._show_placeholder()

    def set_placeholder(self, text):
        self.delete(0, ctk.END)
        self._placeholder_text = text
        self._show_placeholder()

    def _on_focus_in(self, event):
        self.delete(0, ctk.END)
        self._placeholder_shown = False
        self.configure(text_color=self._text_color)  # Reset to normal text color

    def _show_placeholder(self):
        self.delete(0, ctk.END)
        self.insert(0, self._placeholder_text)
        self.configure(text_color='gray')  # Make placeholder gray
        self._placeholder_shown = True

    def get(self):
        # Don't return the placeholder text as the actual value
        if self._placeholder_shown:
            return ''
        return super().get()

    def insert(self, index, string):
        if self._placeholder_shown:
            self.delete(0, ctk.END)
            self._placeholder_shown = False
            self.configure(text_color=self._text_color)
        super().insert(index, string)

    def _on_key_release(self, event):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

        if not self.get():  # If entry is empty
            return

        text = self.get().lower()
        # First show exact prefix matches, then contains matches
        exact_matches = [s for s in self.suggestions if s.lower().startswith(text)]
        contains_matches = [s for s in self.suggestions if text in s.lower() and not s.lower().startswith(text)]

        suggestions = sorted(exact_matches) + sorted(contains_matches)

        if suggestions:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()

            self.suggestion_window = ctk.CTkToplevel()
            self.suggestion_window.withdraw()  # Hide initially
            self.suggestion_window.overrideredirect(True)

            self.suggestion_listbox = ctk.CTkScrollableFrame(self.suggestion_window)
            self.suggestion_listbox.pack(fill="both", expand=True)

            for suggestion in suggestions:
                suggestion_button = ctk.CTkButton(
                    self.suggestion_listbox,
                    text=suggestion,
                    command=lambda s=suggestion: self._select_suggestion(s)
                )
                suggestion_button.pack(fill="x", padx=2, pady=1)

            self.suggestion_window.geometry(f"{self.winfo_width()}x300+{x}+{y}")
            self.suggestion_window.deiconify()  # Show window

    def _select_suggestion(self, suggestion):
        self.delete(0, "end")
        self.insert(0, suggestion)
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        # Trigger the callback if it exists
        if hasattr(self, 'callback') and self.callback:
            self.callback(suggestion)

    def _on_focus_out(self, event):
        # Add a small delay before destroying the window
        if self.suggestion_window:
            self.after(100, self._destroy_suggestion_window)

    def _destroy_suggestion_window(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
