from version_finder import VersionFinder, GitError, GitCommandError, InvalidCommitError, InvalidSubmoduleError, InvalidBranchError, GitNotInstalledError
from version_finder.__common__ import parse_arguments
from version_finder import setup_logger
from version_finder import LoggerProtocol
import logging
import os
import argparse
from PIL import Image, ImageTk
import customtkinter as ctk


def check_tkinter():
    try:
        import tkinter
        return True
    except ImportError:
        return False


def install_tkinter():
    import platform
    system = platform.system().lower()

    if system == "linux":
        os.system("sudo apt-get install python3-tk")
    elif system == "darwin":  # MacOS
        os.system("brew install python-tk")
    elif system == "windows":
        os.system("pip install tk")


def launch_gui():
    if not check_tkinter():
        install_tkinter()


launch_gui()


os.environ['TK_SILENCE_DEPRECATION'] = '1'

__gui_version__ = '2.0.0'


class AutocompleteEntry(ctk.CTkEntry):
    def __init__(self, *args, placeholder_text=None, **kwargs):
        self.suggestions = kwargs.pop('suggestions', [])
        super().__init__(*args, placeholder_text=placeholder_text, **kwargs)

        self._placeholder_text = placeholder_text
        self._placeholder_shown = True

        self.suggestion_window = None
        self.suggestion_listbox = None

        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._on_focus_out)

        # Initialize placeholder if provided
        if self._placeholder_text:
            self._show_placeholder()


    def set_placeholder(self, text):
        self._placeholder_text = text
        if self._placeholder_shown:
            self._show_placeholder()

    def _on_focus_in(self, event):
        if self._placeholder_shown:
            self.delete(0, 'end')
            self._placeholder_shown = False
            self.configure(text_color=self._text_color)  # Reset to normal text color

    def _show_placeholder(self):
        self.delete(0, 'end')
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
            self.delete(0, 'end')
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


class VersionFinderGUI(ctk.CTk):
    def __init__(self, path: str = None, logger: LoggerProtocol = None):
        super().__init__()
        self.repo_path = path
        self.version_finder = None
        self.logger = logger or setup_logger("VersionFinderGUI", logging.INFO)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        self.setup_icon()
        self.setup_window()
        self.center_window()

        # Create main_frame before creating widgets
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_widgets()
        if self.repo_path:
            self.browse_directory()

    def setup_window(self):
        self.title("Version Finder")
        self.window_height = 800
        self.window_width = 700
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.minsize(650, 400)
        self.maxsize(1200, 900)
        self.focus_force()

        self.configure(fg_color=("gray95", "gray10"))  # Adaptive background



    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # Replace the existing header with this
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(20, 10))

        header = ctk.CTkLabel(
            header_frame,
            text="Version Finder",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("green", "lightgreen")  # Adaptive color
        )
        header.pack(side="top")

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

        commit_label = ctk.CTkLabel(commit_frame, text="Commit SHA", width=100, font=ctk.CTkFont(size=16, weight="bold"), anchor="w", justify="left")
        commit_label.pack(side="left", padx=5, pady=10)

        self.commit_entry = ctk.CTkEntry(commit_frame, width=300, placeholder_text="Required")
        self.commit_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)

    def create_directory_section(self):
        dir_frame = ctk.CTkFrame(self.main_frame)
        dir_frame.pack(fill="x", padx=10, pady=10)

        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Select Directory:",
            width=100,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("black", "white")  # Adaptive text color
        )
        dir_label.pack(side="left", padx=5)

        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            width=240,
            border_width=1,
            corner_radius=10
        )
        self.dir_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self.browse_directory_btn,
            width=100,
            corner_radius=10,
            hover_color=("green", "darkgreen")  # Adaptive hover color
        )
        browse_btn.pack(side="right", padx=10, pady=10)

    def _on_branch_select(self, branch):
        try:
            self.version_finder.update_repository(branch)
            self.output_text.insert("end", f"✅ Repository updated to branch: {branch}\n")
            self.output_text.see("end")
            if self.version_finder.list_submodules():
                self.output_text.insert("end", "✅ Submodules found.\n")
                self.output_text.see("end")
                self.submodule_entry.set_placeholder("Optional: Select a submodule")
            else:
                self.submodule_entry.set_placeholder("No submodules found")
        except Exception as e:
            self.output_text.insert("end", f"❌ Error updating repository: {str(e)}\n")
            self.output_text.see("end")

    def create_branch_selection(self):
        branch_frame = ctk.CTkFrame(self.main_frame)
        branch_frame.pack(fill="x", padx=10, pady=10)

        branch_label = ctk.CTkLabel(branch_frame, text="Branch", width=100, font=ctk.CTkFont(size=16, weight="bold"), anchor="w", justify="left")
        branch_label.pack(side="left", padx=5)

        self.branch_entry = AutocompleteEntry(
            branch_frame,
            width=240,
            placeholder_text="Enter branch name..."
        )
        self.branch_entry.callback = self._on_branch_select  # Add callback
        self.branch_entry.pack(fill="x", padx=10, pady=10, expand=True)
        self.branch_entry.configure(state="disabled")

    def create_submodule_selection(self):
        submodule_frame = ctk.CTkFrame(self.main_frame)
        submodule_frame.pack(fill="x", padx=10, pady=10)

        submodule_label = ctk.CTkLabel(submodule_frame, text="Submodule", width=100,
                                       font=ctk.CTkFont(size=16, weight="bold"))
        submodule_label.pack(side="left", padx=5)

        self.submodule_entry = AutocompleteEntry(
            submodule_frame,
            width=300,
            placeholder_text='Optional: Select a submodule'
        )
        self.submodule_entry.pack(fill="x", padx=10, pady=10, expand=True)
        self.submodule_entry.configure(state="disabled")

    def create_output_area(self):
        output_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        output_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.output_text = ctk.CTkTextbox(
            output_frame,
            wrap="word",
            font=("Courier New", 11),  # Monospaced font for logs
            border_width=1,
            corner_radius=10,
            fg_color=("white", "gray15"),  # Adaptive background
            text_color=("black", "white"),  # Adaptive text color
            scrollbar_button_color=("gray80", "gray30")
        )
        self.output_text.pack(fill="both", expand=True)

    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=10)

        # Create a gradient effect with multiple buttons
        search_btn = ctk.CTkButton(
            button_frame,
            text="Search",
            command=self.search,
            corner_radius=10,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "forestgreen")
        )
        search_btn.pack(side="left", padx=5, expand=True, fill="x")

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            command=self.clear_output,
            corner_radius=10,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        clear_btn.pack(side="left", padx=5, expand=True, fill="x")

        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.quit,
            corner_radius=10,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "firebrick")
        )
        exit_btn.pack(side="right", padx=5, expand=True, fill="x")

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
            self.version_finder = VersionFinder(self.dir_entry.get(), logger=self.logger)
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
            directory = ctk.filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.initialize_version_finder()

            self.branch_entry.suggestions = self.version_finder.list_branches()
            self.branch_entry.configure(state="normal")

            self.submodule_entry.suggestions = self.version_finder.list_submodules()
            self.submodule_entry.configure(state="normal")

    def validate_entries(self):
        required_fields = {
            "Directory": self.dir_entry.get().strip(),
            "Branch": self.branch_entry.get().strip(),
            "Commit": self.commit_entry.get().strip(),
        }

        valid_input = True
        for field_name, value in required_fields.items():
            if not value:
                self.output_text.insert("end", f"⚠️ {field_name} is required.\n")
                valid_input = False
            else:
                # Add logic to check if the value is a valid branch or commit
                pass

        return valid_input

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
                result = self.version_finder.find_first_version_containing_commit(
                    self.version_finder.get_commit_sha_from_relative_string(commit), submodule)
                self.output_text.insert("end", f"✅ Search completed successfully: The version is {result}\n")
            except InvalidCommitError as e:
                self.output_text.insert("end", f"❌ Error: {str(e)}\n")
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

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(name=__name__, level=log_level)
    app = VersionFinderGUI(args.path, logger=logger)
    app.mainloop()


def main():
    args = parse_arguments()
    gui_main(args)


if __name__ == "__main__":
    main()
