import os
import customtkinter as ctk


# def check_tkinter():
#     try:
#         import tkinter
#         return True
#     except ImportError:
#         return False


# def install_tkinter():
#     import platform
#     system = platform.system().lower()

#     if system == "linux":
#         os.system("sudo apt-get install python3-tk")
#     elif system == "darwin":  # MacOS
#         os.system("brew install python-tk")
#     elif system == "windows":
#         os.system("pip install tk")


# def launch_gui():
#     if not check_tkinter():
#         install_tkinter()


# launch_gui()


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
