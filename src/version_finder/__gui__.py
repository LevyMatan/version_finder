import customtkinter as ctk
from PIL import Image, ImageTk
import argparse
import os
from .__common__ import parse_arguments
from .core import VersionFinder, GitError, GitCommandError

os.environ['TK_SILENCE_DEPRECATION'] = '1'

__gui_version__ = '1.0.0'


class AutocompleteEntry(ctk.CTkEntry):
    def __init__(self, *args, **kwargs):
        self.suggestions = kwargs.pop('suggestions', [])
        super().__init__(*args, **kwargs)

        self.suggestion_window = None
        self.suggestion_listbox = None

        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._on_focus_out)

    def _on_key_release(self, event):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

        if not self.get():  # If entry is empty
            return

        text = self.get().lower()
        suggestions = [s for s in self.suggestions if text in s.lower()]

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

            self.suggestion_window.geometry(f"{self.winfo_width()}x150+{x}+{y}")
            self.suggestion_window.deiconify()  # Show window

    def _select_suggestion(self, suggestion):
        self.delete(0, "end")
        self.insert(0, suggestion)
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

    def _on_focus_out(self, event):
        # Add a small delay before destroying the window
        if self.suggestion_window:
            self.after(100, self._destroy_suggestion_window)

    def _destroy_suggestion_window(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None


class VersionFinderGUI(ctk.CTk):
    def __init__(self, path: str = None):
        super().__init__()
        self.repo_path = path
        self.version_finder = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.setup_icon()
        self.setup_window()
        self.center_window()
        self.create_widgets()
        if self.repo_path:
            self.browse_directory()

    def setup_window(self):
        self.title("Version Finder")
        self.window_height = 1000
        self.window_width = 600
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.minsize(600, 400)
        self.maxsize(1200, 800)
        self.focus_force()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="Version Finder",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)

        # Directory selection
        self.create_directory_section()
        # Branch selection (initially disabled)
        self.create_branch_selection()
        # Submodule selection (initially disabled)
        self.create_submodule_selection()
        # Commit section
        self.create_commit_section()

        # Output area
        self.create_output_area()

        # Buttons
        self.create_buttons()

    def create_commit_section(self):
        commit_frame = ctk.CTkFrame(self.main_frame)
        commit_frame.pack(fill="x", padx=10, pady=10)

        commit_label = ctk.CTkLabel(commit_frame, text="Commit:")
        commit_label.pack(side="left", padx=5)

        self.commit_entry = ctk.CTkEntry(commit_frame, width=300)
        self.commit_entry.pack(side="left", padx=5, fill="x", expand=True)

    def create_directory_section(self):
        dir_frame = ctk.CTkFrame(self.main_frame)
        dir_frame.pack(fill="x", padx=10, pady=10)

        dir_label = ctk.CTkLabel(dir_frame, text="Select Directory:")
        dir_label.pack(side="left", padx=5)

        self.dir_entry = ctk.CTkEntry(dir_frame, width=300)
        self.dir_entry.pack(side="left", padx=5, fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self.browse_directory_btn,
            width=100
        )
        browse_btn.pack(side="right", padx=5)

    def create_branch_selection(self):
        branch_frame = ctk.CTkFrame(self.main_frame)
        branch_frame.pack(fill="x", padx=10, pady=10)

        branch_label = ctk.CTkLabel(branch_frame, text="Branch:")
        branch_label.pack(side="left", padx=5)

        self.branch_entry = AutocompleteEntry(
            branch_frame,
            width=240,
        )
        self.branch_entry.pack(fill="x", padx=10, pady=10, expand=True)
        self.branch_entry.configure(state="disabled")

    def create_submodule_selection(self):
        submodule_frame = ctk.CTkFrame(self.main_frame)
        submodule_frame.pack(fill="x", padx=10, pady=10)

        submodule_label = ctk.CTkLabel(submodule_frame, text="Submodule:")
        submodule_label.pack(side="left", padx=5)

        self.submodule_entry = AutocompleteEntry(
            submodule_frame,
            width=300,
        )
        self.submodule_entry.pack(fill="x", padx=10, pady=10, expand=True)
        self.submodule_entry.configure(state="disabled")

    def create_output_area(self):
        output_frame = ctk.CTkFrame(self.main_frame)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_text = ctk.CTkTextbox(
            output_frame,
            wrap="word",
            font=("Helvetica", 11)
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        search_btn = ctk.CTkButton(
            button_frame,
            text="Search",
            command=self.search
        )
        search_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            command=self.clear_output
        )
        clear_btn.pack(side="left", padx=5)

        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.quit
        )
        exit_btn.pack(side="right", padx=5)

    def setup_icon(self):
        # Set the icon for the application
        icon_path = os.path.join(os.path.dirname(__file__), 'assets/icon.png')
        if os.path.exists(icon_path):
            # Load the image
            icon = Image.open(icon_path)
            icon = ImageTk.PhotoImage(icon)

            # Set the icon
            self.wm_iconphoto(True, icon)

    def initialize_version_finder(self):
        try:
            self.version_finder = VersionFinder(self.dir_entry.get())
            self.output_text.insert("end", "✅ Repository loaded successfully\n")
        except GitError as e:
            self.output_text.insert("end", f"❌ Error: {str(e)}\n")

    def browse_directory_btn(self):
        self.repo_path = None
        self.browse_directory()

    def browse_directory(self):
        if self.repo_path:
            directory = self.repo_path
        else:
            directory = ctk.filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.initialize_version_finder()

            self.branch_entry.suggestions = self.version_finder.get_branches()
            self.branch_entry.configure(state="normal")

            self.submodule_entry.suggestions = self.version_finder.get_submodules()
            self.submodule_entry.configure(state="normal")

    def validate_entries(self):
        required_fields = {
            "Directory": self.dir_entry.get().strip(),
            "Branch": self.branch_entry.get().strip(),
            "Commit": self.commit_entry.get().strip(),
        }

        for field_name, value in required_fields.items():
            if not value:
                self.output_text.insert("end", f"⚠️ {field_name} is required.\n")
                return False

        return True

    def search(self):
        try:
            directory = self.dir_entry.get()
            if not directory:
                self.output_text.insert("end", "⚠️ Please select a directory first.\n")
                return

            if not self.validate_entries():
                self.output_text.insert("end", "⚠️ Please fill in all required fields.\n")
                self.output_text.see("end")
                return

            # Get values from entries
            branch = self.branch_entry.get()
            submodule = self.submodule_entry.get()
            commit = self.commit_entry.get()

            # Display search parameters
            self.output_text.insert("end", f"🔍 Searching in: {directory}\n")
            self.output_text.insert("end", f"Branch: {branch}\n")
            self.output_text.insert("end", f"Submodule: {submodule}\n")
            self.output_text.insert("end", f"Commit: {commit}\n")

            # Perform the search with error handling
            try:
                result = self.version_finder.get_version_of_commit(branch, commit, submodule)
                self.output_text.insert("end", f"✅ Search completed successfully: The version is {result}\n")
            except GitCommandError as e:
                self.output_text.insert("end", f"❌ Git Error: {str(e)}\n")
            except Exception as e:
                self.output_text.insert("end", f"❌ Error: An unexpected error occurred - {str(e)}\n")

            self.output_text.see("end")

        except Exception as e:
            self.output_text.insert("end", f"❌ System Error: {str(e)}\n")
            self.output_text.see("end")

    def clear_output(self):
        self.output_text.delete("1.0", "end")


def gui_main(args: argparse.Namespace) -> int:
    if args.version:
        print(f"Version: {__gui_version__}")
        return 0

    app = VersionFinderGUI(args.path)
    app.mainloop()


def main():
    args = parse_arguments()
    gui_main(args)


if __name__ == "__main__":
    main()
