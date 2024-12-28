import customtkinter as ctk
import os
import argparse
from pathlib import Path
from enum import Enum, auto
from typing import List
import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.resources
from version_finder.version_finder import VersionFinder, Commit
from version_finder.common import parse_arguments
from version_finder.logger import setup_logger
from version_finder_gui.widgets import AutocompleteEntry, CommitListWindow, center_window


class VersionFinderTasks(Enum):
    FIND_VERSION = auto()
    COMMITS_BETWEEN_VERSIONS = auto()
    COMMITS_BY_TEXT = auto()


ctk.set_default_color_theme("green")


class VersionFinderGUI(ctk.CTk):
    def __init__(self, path: str = ''):
        super().__init__()
        self.repo_path = Path(path).resolve() if path else path
        self.logger = setup_logger()
        self.title("Version Finder")
        self.version_finder: VersionFinder = None
        self.selected_branch: str = ''
        self.selected_submodule: str = ''
        # Initialize UI
        self._setup_window()
        self._create_window_layout()
        self._setup_icon()
        self._show_find_version()
        # Center window on screen
        center_window(self)

        # Focous on window
        self.focus_force()

        if self.repo_path:
            self._initialize_version_finder()

    def _setup_window(self):
        """Configure the main window settings"""
        self.geometry("1200x800")
        self.minsize(800, 600)

    def _create_window_layout(self):
        """Create the main layout with sidebar and content area"""
        # Configure grid weights for the main window
        self.grid_columnconfigure(0, weight=0)  # Sidebar column (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Content column (expandable)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(0, weight=1)
        self.sidebar_content_frame = self._create_sidebar(self.sidebar_frame)
        self.sidebar_content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)

        # Create main area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame = self._create_content_area(self.main_frame)
        self.main_content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)

    def _create_sidebar(self, parent_frame):
        """Create the sidebar with task selection buttons"""

        sidebar_content_frame = ctk.CTkFrame(parent_frame)
        # Configure sidebar grid
        sidebar_content_frame.grid_columnconfigure(0, weight=1)
        sidebar_content_frame.grid_rowconfigure(2, weight=1)

        # App title
        title = ctk.CTkLabel(
            sidebar_content_frame,
            text="Choose Task",
            font=("Arial", 20, "bold")
        )
        title.grid(row=0, column=0, pady=[10, 30], padx=10)

        sidebar_task_buttons_frame = ctk.CTkFrame(sidebar_content_frame, fg_color="transparent")
        sidebar_task_buttons_frame.grid(row=1, column=0, sticky="nsew")
        # Task selection buttons
        tasks = [
            ("Find Version", self._show_find_version),
            ("Find Commits", self._show_find_commits),
            ("Search Commits", self._show_search_commits)
        ]

        for idx, (text, command) in enumerate(tasks, start=1):
            btn = ctk.CTkButton(
                sidebar_task_buttons_frame,
                text=text,
                command=command,
                width=180,
            )
            btn.grid(row=idx, column=0, pady=5, padx=10)

        # Add configuration button at the bottom
        config_btn = ctk.CTkButton(
            sidebar_content_frame,
            text="⚙️ Settings",
            command=self._show_configuration,
            width=180
        )
        config_btn.grid(row=2, column=0, pady=15, padx=10, sticky="s")
        return sidebar_content_frame

    def _create_header_frame(self, parent_frame):
        """Create the header frame"""
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        # Header title
        header = ctk.CTkLabel(
            header_frame,
            text="Version Finder",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#76B900"
        )
        header.grid(row=0, column=0, padx=20, pady=10)
        return header_frame

    def _create_content_area(self, parent_frame):
        """
        Create the main content area with constant widgets
        # main_content_frame
        ####################
        # Row - 0: hear frame
        # Row - 1: content frame
            # content frame
            ###############
            # Row - 0: directory frame
            # Row - 1: branch input frame
            # Row - 2: submodule input frame
            # Row - 3: Task input frame
            # Row - 4: Operation buttons frame
            # Row - 5: Output frame
        """
        main_content_frame = ctk.CTkFrame(parent_frame)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1)

        # Configure header frame grid
        header_frame = self._create_header_frame(main_content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Configure content frame grid
        content_frame = ctk.CTkFrame(main_content_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(5, weight=10)

        # Directory selection
        dir_frame = self._create_directory_section(content_frame)
        dir_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=[10, 5])

        # Branch selection
        branch_frame = self._create_branch_selection(content_frame)
        branch_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        # Submodule selection
        submodule_frame = self._create_submodule_selection(content_frame)
        submodule_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)

        # Task-specific content frame
        self.task_frame = ctk.CTkFrame(content_frame)
        self.task_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=5)

        app_buttons_frame = self._create_app_buttons(content_frame)
        app_buttons_frame.grid(row=4, column=0, sticky="nsew", padx=15, pady=15)

        # Output area
        output_frame = self._create_output_area(content_frame)
        output_frame.grid(row=5, column=0, sticky="nsew", padx=15, pady=10)

        return main_content_frame

    def _create_directory_section(self, parent_frame):
        """Create the directory selection section"""
        dir_frame = ctk.CTkFrame(parent_frame)
        dir_frame.grid(row=0, column=0, sticky="ew", pady=15)
        dir_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dir_frame, text="Repository Path:").grid(row=0, column=0, padx=5)
        self.dir_entry = ctk.CTkEntry(dir_frame, width=400, placeholder_text="Enter repository path")
        self.dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self._browse_directory
        )
        browse_btn.grid(row=0, column=2, padx=5)
        return dir_frame

    def _update_submodule_entry(self, submodules):
        # First ensure the widget is in normal state
        self.submodule_entry.configure(state="normal")
        if submodules:
            self.submodule_entry.set_placeholder("Select a submodule [Optional]")
            self.submodule_entry.suggestions = submodules
            self._log_output("Loaded submodules successfully.")
        else:
            self.submodule_entry.set_placeholder("No submodules found")
            self._log_output("There are no submodules in the repository (with selected branch).")
            # Set readonly state last
            self.submodule_entry.configure(state="readonly")

        self.submodule_entry.after(100, self.submodule_entry.update)

    def _on_branch_select(self, branch):
        if self.version_finder is None:
            self._log_error("System error: trying to access unintialized variable")
            raise Exception("System error: trying to access unintialized variable: version_finder")
        try:
            self.selected_branch = branch
            self.selected_submodule = ''
            self.version_finder.update_repository(branch)
            self._log_output(f"Repository updated to branch: {self.selected_branch}")
            self._update_submodule_entry(self.version_finder.list_submodules())

        except Exception as e:
            self._log_error(f"Error updating repository: {str(e)}")

    def _on_submodule_select(self, submodule):
        if self.version_finder is None:
            self._log_error("System error: trying to access unintialized variable")
            raise Exception("System error: trying to access unintialized variable: version_finder")
        try:
            self.selected_submodule = submodule
        except Exception as e:
            self._log_error(f"Error updating repository: {str(e)}")

    def _create_branch_selection(self, parent_frame):
        """Create the branch selection section"""
        branch_frame = ctk.CTkFrame(parent_frame)
        branch_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(branch_frame, text="Branch:").grid(row=0, column=0, padx=5)
        self.branch_entry = AutocompleteEntry(branch_frame, width=400, placeholder_text="Select a branch")
        self.branch_entry.configure(state="disabled")
        self.branch_entry.callback = self._on_branch_select

        self.branch_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        return branch_frame

    def _create_submodule_selection(self, parent_frame):
        """Create the submodule selection section"""
        submodule_frame = ctk.CTkFrame(parent_frame)
        submodule_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(submodule_frame, text="Submodule:").grid(row=0, column=0, padx=5)
        self.submodule_entry = AutocompleteEntry(
            submodule_frame, width=400, placeholder_text='Select a submodule [Optional]')
        self.submodule_entry.configure(state="disabled")
        self.submodule_entry.callback = self._on_submodule_select
        self.submodule_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        return submodule_frame

    def _create_app_buttons(self, parent_frame):
        buttons_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")

        # Create a gradient effect with multiple buttons
        search_btn = ctk.CTkButton(
            buttons_frame,
            text="Search",
            command=self._search,
            corner_radius=10,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "forestgreen")
        )
        search_btn.pack(side="left", padx=5, expand=True, fill="x")

        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear",
            command=self._clear_output,
            corner_radius=10,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        clear_btn.pack(side="left", padx=5, expand=True, fill="x")

        exit_btn = ctk.CTkButton(
            buttons_frame,
            text="Exit",
            command=self.quit,
            corner_radius=10,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "firebrick")
        )
        exit_btn.pack(side="right", padx=5, expand=True, fill="x")
        return buttons_frame

    def _create_output_area(self, parent_frame):
        """Create the output/logging area"""
        output_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.output_text = ctk.CTkTextbox(
            output_frame,
            wrap="word",
            height=200,
            font=("Arial", 12),
            border_width=1,
            corner_radius=10,
            scrollbar_button_color=("gray80", "gray30")
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        return output_frame

    def _clear_output(self):
        self.output_text.delete("1.0", "end")

    def _show_configuration(self):
        """Show the configuration window"""
        config_window = tk.Toplevel(self)
        config_window.title("Settings")
        config_window.geometry("400x300")

        center_window(config_window)

        # Add your configuration options here
        # For example:
        config_frame = ctk.CTkFrame(config_window)
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Theme selection
        theme_label = ctk.CTkLabel(config_frame, text="Theme Settings", font=("Arial", 16, "bold"))
        theme_label.pack(pady=(15, 10))

        theme_var = tk.StringVar(value="Dark")
        theme_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Light", "Dark", "System"],
            variable=theme_var,
            command=lambda x: ctk.set_appearance_mode(x)
        )
        theme_menu.pack(pady=15)

        # Apply button
        apply_btn = ctk.CTkButton(
            config_frame,
            text="Apply Settings",
            command=self._apply_settings,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "forestgreen")
        )
        apply_btn.pack(pady=15)
        self.config_window = config_window

    def _apply_settings(self):
        """Apply configuration settings and return to previous view"""
        # You can add more configuration logic here
        self._log_output("Settings applied successfully!")
        # Return to the last active task view
        if hasattr(self, 'current_displayed_task'):
            if self.current_displayed_task == VersionFinderTasks.FIND_VERSION:
                self._show_find_version()
            elif self.current_displayed_task == VersionFinderTasks.COMMITS_BETWEEN_VERSIONS:
                self._show_find_commits()
            elif self.current_displayed_task == VersionFinderTasks.COMMITS_BY_TEXT:
                self._show_search_commits()
        self.config_window.destroy()

    def _show_find_version(self):
        """Show the find version task interface"""
        self._clear_task_frame()
        ctk.CTkLabel(self.task_frame, text="Commit SHA:").grid(row=0, column=0, padx=5)
        self.commit_entry = ctk.CTkEntry(self.task_frame, width=400, placeholder_text="Required")
        self.commit_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.task_frame.grid_columnconfigure(1, weight=1)
        self.current_displayed_task = VersionFinderTasks.FIND_VERSION

    def _show_find_commits(self):
        """Show the find commits between versions task interface"""
        self._clear_task_frame()

        ctk.CTkLabel(self.task_frame, text="Start Version:").grid(row=0, column=0, padx=5)
        self.start_version_entry = ctk.CTkEntry(self.task_frame, width=400, placeholder_text="Required")
        self.start_version_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(self.task_frame, text="End Version:").grid(row=0, column=2, padx=5)
        self.end_version_entry = ctk.CTkEntry(self.task_frame, width=400, placeholder_text="Required")
        self.end_version_entry.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.current_displayed_task = VersionFinderTasks.COMMITS_BETWEEN_VERSIONS

    def _show_search_commits(self):
        """Show the search commits by text task interface"""
        self._clear_task_frame()

        ctk.CTkLabel(self.task_frame, text="Search Pattern:").grid(row=0, column=0, padx=5)
        self.search_text_pattern_entry = ctk.CTkEntry(self.task_frame, width=400, placeholder_text="Required")
        self.search_text_pattern_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.task_frame.grid_columnconfigure(1, weight=1)
        self.current_displayed_task = VersionFinderTasks.COMMITS_BY_TEXT

    def _clear_task_frame(self):
        """Clear the task-specific frame"""
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        # self.task_frame.grid_forget()

    def _browse_directory(self):
        """Open directory browser dialog"""
        self.repo_path = None
        directory = filedialog.askdirectory(initialdir=Path.cwd())
        if directory:
            # Clear directory entry
            self.dir_entry.delete(0, tk.END)

            # Clear branch entry
            self.branch_entry.delete(0, tk.END)

            # Clear submodule entry
            self.submodule_entry.delete(0, tk.END)
            self.repo_path = directory
            self._initialize_version_finder()

    def _update_branch_entry(self):
        """Update the branch entry with the current branch"""
        if self.version_finder:
            self.branch_entry.suggestions = self.version_finder.list_branches()
            self.branch_entry.configure(state="normal")
            self.selected_branch = self.version_finder.get_current_branch()
            if self.selected_branch:
                self.branch_entry.delete(0, tk.END)
                self.branch_entry.insert(0, self.selected_branch)
                self._log_output("Loaded branches successfully.")
                self._on_branch_select(self.selected_branch)

    def _initialize_version_finder(self):
        """Initialize the VersionFinder instance"""
        if not self.repo_path:
            self._log_error("Invalid repository path.")
            return
        try:
            self.version_finder = VersionFinder(self.repo_path.__str__())
            self._log_output(f"VersionFinder initialized with: {self.repo_path} successfully.")
            self.dir_entry.insert(0, self.repo_path)

            # Update branch autocomplete
            self._update_branch_entry()

            # Update submodule autocomplete
            self._update_submodule_entry(self.version_finder.list_submodules())

        except Exception as e:
            self._log_error(str(e))

    def ensure_version_finder_initialized(func):
        def wrapper(self, *args, **kwargs):
            if self.version_finder is None:
                self._log_error("System error: trying to access unintialized variable")
                raise Exception("System error: trying to access unintialized variable: version_finder")
            return func(self, *args, **kwargs)
        return wrapper

    @ensure_version_finder_initialized
    def _search_version_by_commit(self):
        try:
            self.version_finder.update_repository(self.selected_branch)
            commit = self.commit_entry.get()
            version = self.version_finder.find_first_version_containing_commit(
                commit,
                submodule=self.selected_submodule
            )
            if version is None:
                self._log_error(f"No version found for commit {commit}, most likely it is too new.")
            else:
                self._log_output(f"Version for commit {commit}: {version}")
        except Exception as e:
            self._log_error(str(e))

    def _search(self):
        """Handle version search"""
        try:
            if not self._validate_inputs():
                return
            if (self.current_displayed_task == VersionFinderTasks.FIND_VERSION):
                self._search_version_by_commit()
            elif (self.current_displayed_task == VersionFinderTasks.COMMITS_BETWEEN_VERSIONS):
                self._search_commits_between()
            elif (self.current_displayed_task == VersionFinderTasks.COMMITS_BY_TEXT):
                self._search_commits_by_text()
        except Exception as e:
            self._log_error(str(e))

    @ensure_version_finder_initialized
    def _search_commits_between(self):
        """Handle commits between versions search"""
        try:

            self.version_finder.update_repository(self.selected_branch)
            commits = self.version_finder.get_commits_between_versions(
                self.start_version_entry.get(),
                self.end_version_entry.get(),
                submodule=self.selected_submodule
            )
            CommitListWindow(self, commits)
        except Exception as e:
            self._log_error(str(e))

    @ensure_version_finder_initialized
    def _search_commits_by_text(self):
        """Handle commits search by text"""
        try:
            if not self._validate_inputs():
                return

            self.version_finder.update_repository(self.selected_branch)
            commits = self.version_finder.find_commits_by_text(
                self.search_text_pattern_entry.get(),
                submodule=self.selected_submodule
            )
            CommitListWindow(self, commits)
        except Exception as e:
            self._log_error(str(e))

    def _validate_inputs(self) -> bool:
        """Validate required inputs"""
        if not self.dir_entry.get():
            messagebox.showerror("Error", "Please select a repository directory")
            return False

        if not self.branch_entry.get():
            messagebox.showerror("Error", "Please select a branch")
            return False

        if not self.version_finder:
            self._initialize_version_finder()
            if not self.version_finder:
                return False

        return True

    def _log_output(self, message: str):
        """Log output message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"✅ {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
        self.logger.debug(message)

    def _log_error(self, message: str):
        """Log error message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"❌ Error: {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
        self.logger.error(message)

    def _setup_icon(self):
        """Setup application icon"""
        try:
            with importlib.resources.path("version_finder_gui.assets", 'icon.png') as icon_path:
                self.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except Exception:
            pass

    def center_window(window):
        """Center the window on the screen"""
        window.update()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")


def gui_main(args: argparse.Namespace) -> int:
    if args.version:
        from .__version__ import __version__
        print(f"version_finder gui-v{__version__}")
        return 0

    _ = setup_logger(verbose=args.verbose)
    app = VersionFinderGUI(args.path)
    app.mainloop()
    return 0


def main():
    args = parse_arguments()
    gui_main(args)


if __name__ == "__main__":
    main()