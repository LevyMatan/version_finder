"""Custom widgets used in the GUI application."""

from typing import Dict, List
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk


class CommitDetailsWindow(ctk.CTkToplevel):
    """Window displaying detailed commit information."""

    def __init__(self, parent, commit_data: Dict):
        super().__init__(parent)
        self.title("Commit Details")
        self.geometry("600x400")

        # Create scrollable frame for commit info
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add commit details
        for key, value in commit_data.items():
            label = ctk.CTkLabel(scroll_frame, text=f"{key}:", anchor="w")
            label.pack(fill="x", pady=2)
            text = ctk.CTkTextbox(scroll_frame, height=50)
            text.insert("1.0", str(value))
            text.configure(state="disabled")
            text.pack(fill="x", pady=(0, 10))


class CommitListWindow(ctk.CTkToplevel):
    """Window displaying a list of commits."""

    def __init__(self, parent, commits: List[Dict]):
        super().__init__(parent)
        self.title("Commit List")
        self.geometry("800x600")

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

    def _add_commit_row(self, commit: Dict):
        """Add a row for a commit in the list."""
        row = ctk.CTkFrame(self.scroll_frame)
        row.pack(fill="x", pady=2)

        hash_btn = ctk.CTkButton(
            row,
            text=commit['hash'][:8],
            width=100,
            command=lambda: self._copy_to_clipboard(commit['hash'])
        )
        hash_btn.pack(side="left", padx=5)

        subject_btn = ctk.CTkButton(
            row,
            text=commit['subject'],
            width=500,
            command=lambda: CommitDetailsWindow(self, commit)
        )
        subject_btn.pack(side="left", padx=5)

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commit hash copied to clipboard!")


class AutocompleteEntry(ctk.CTkEntry):
    """Entry widget with autocompletion functionality."""

    def __init__(self, *args, completion_list=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.completion_list = completion_list or []
        self.popup_window = None
        self.listbox = None

        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._on_focus_out)

    def set_completion_list(self, completion_list: List[str]):
        """Set the list of completion options."""
        self.completion_list = completion_list

    def _on_key_release(self, event):
        """Handle key release event for autocompletion."""
        if event.keysym in ('Up', 'Down', 'Return'):
            if self.popup_window:
                self._handle_selection(event.keysym)
            return

        self._show_suggestions()

    def _show_suggestions(self):
        """Show suggestion popup window."""
        value = self.get().lower()
        if not value:
            self._destroy_popup()
            return

        suggestions = [
            item for item in self.completion_list
            if value in item.lower()
        ]

        if not suggestions:
            self._destroy_popup()
            return

        if not self.popup_window:
            self._create_popup()

        self.listbox.delete(0, tk.END)
        for item in suggestions:
            self.listbox.insert(tk.END, item)

    def _create_popup(self):
        """Create the popup window for suggestions."""
        self.popup_window = tk.Toplevel()
        self.popup_window.overrideredirect(True)
        self.popup_window.lift()

        self.listbox = tk.Listbox(
            self.popup_window,
            selectmode=tk.SINGLE,
            height=5
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.popup_window.geometry(f"+{x}+{y}")

    def _handle_selection(self, key):
        """Handle selection from suggestion list."""
        if not self.listbox:
            return

        if key == 'Up':
            if self.listbox.curselection():
                index = self.listbox.curselection()[0]
                if index > 0:
                    self.listbox.select_clear(index)
                    self.listbox.select_set(index - 1)
        elif key == 'Down':
            if self.listbox.curselection():
                index = self.listbox.curselection()[0]
                if index < self.listbox.size() - 1:
                    self.listbox.select_clear(index)
                    self.listbox.select_set(index + 1)
            else:
                self.listbox.select_set(0)
        elif key == 'Return':
            if self.listbox.curselection():
                self.delete(0, tk.END)
                self.insert(0, self.listbox.get(self.listbox.curselection()))
                self._destroy_popup()

    def _on_focus_out(self, event):
        """Handle focus out event."""
        # Delay popup destruction to allow for mouse click
        self.after(100, self._destroy_popup)

    def _destroy_popup(self):
        """Destroy the suggestion popup window."""
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None
            self.listbox = None
