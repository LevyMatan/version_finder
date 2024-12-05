import customtkinter as ctk
import os
from enum import Enum, auto
from typing import List
import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.resources
from version_finder import VersionFinder, Commit
from gui import AutocompleteEntry  # We'll reuse this class as it's well-implemented


class CommitDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent, commit_data: Commit):
        super().__init__(parent)
        self.title("Commit Details")
        self.geometry("600x400")

        # Create scrollable frame for commit info
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add commit details
        for key, value in commit_data.__dict__.items():
            label = ctk.CTkLabel(scroll_frame, text=f"{key}:", anchor="w")
            label.pack(fill="x", pady=2)
            text = ctk.CTkTextbox(scroll_frame, height=50)
            text.insert("1.0", str(value))
            text.configure(state="disabled")
            text.pack(fill="x", pady=(0, 10))


class CommitListWindow(ctk.CTkToplevel):
    def __init__(self, parent, commits: List[Commit]):
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

    def _add_commit_row(self, commit: Commit):
        row = ctk.CTkFrame(self.scroll_frame)
        row.pack(fill="x", pady=2)

        hash_btn = ctk.CTkButton(
            row,
            text=commit.sha[:8],
            width=100,
            command=lambda: self._copy_to_clipboard(commit.sha)
        )
        hash_btn.pack(side="left", padx=5)

        subject_btn = ctk.CTkButton(
            row,
            text=commit.subject,
            width=500,
            command=lambda: CommitDetailsWindow(self, commit)
        )
        subject_btn.pack(side="left", padx=5)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commit hash copied to clipboard!")


class VersionFinderTasks(Enum):
    FIND_VERSION = auto()
    COMMITS_BETWEEN_VERSIONS = auto()
    COMMITS_BY_TEXT = auto()


class VersionFinderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Version Finder")
        self.current_task_frame = None
        self.version_finder = None
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        # Initialize UI
        self._setup_window()
        self._create_window_layout()
        self._setup_icon()
        self._show_find_version()
        # Center window on screen
        self.center_window()

        # Focous on window
        self.focus_force()

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

    def _on_branch_select(self, branch):
        try:
            self.version_finder.update_repository(branch)
            self.output_text.insert("end", f"✅ Repository updated to branch: {branch}\n")
            self.output_text.see("end")
            if self.version_finder.list_submodules():
                self.output_text.insert("end", "✅ Submodules found.\n")
                self.output_text.see("end")
                self.submodule_entry.set_placeholder("Select a submodule [Optional]")
            else:
                self.submodule_entry.set_placeholder("No submodules found")
        except Exception as e:
            self.output_text.insert("end", f"❌ Error updating repository: {str(e)}\n")
            self.output_text.see("end")

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

        # Add your configuration options here
        # For example:
        config_frame = ctk.CTkFrame(config_window)
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Theme selection
        theme_label = ctk.CTkLabel(config_frame, text="Theme:")
        theme_label.pack(pady=15)

        theme_var = tk.StringVar(value="Dark")
        theme_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Light", "Dark", "System"],
            variable=theme_var,
            command=lambda x: ctk.set_appearance_mode(x)
        )
        theme_menu.pack(pady=15)

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
        directory = filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self._initialize_version_finder()

    def _initialize_version_finder(self):
        """Initialize the VersionFinder instance"""
        try:
            self.version_finder = VersionFinder(self.dir_entry.get())
            self._log_output("VersionFinder initialized successfully.")
            # Update branch autocomplete
            self.branch_entry.suggestions = self.version_finder.list_branches()
            self.branch_entry.configure(state="normal")
            self._log_output("Loaded branches successfully.")

            # Update submodule autocomplete
            self.submodule_entry.suggestions = self.version_finder.list_submodules()
            if self.submodule_entry.suggestions:
                self.submodule_entry.configure(state="readonly")
                self._log_output("There are no submodules in the repository (with selected branch).")
            else:
                self.submodule_entry.configure(state="normal")
                self._log_output("Loaded submodules successfully.")

        except Exception as e:
            self._log_error(str(e))

    def _search_version_by_commit(self):
        try:
            self.version_finder.update_repository(self.branch_entry.get())
            commit = self.commit_entry.get()
            version = self.version_finder.find_first_version_containing_commit(
                commit,
                submodule=self.submodule_entry.get()
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

    def _search_commits_between(self):
        """Handle commits between versions search"""
        try:

            self.version_finder.update_repository(self.branch_entry.get())
            commits = self.version_finder.get_commits_between_versions(
                self.start_version_entry.get(),
                self.end_version_entry.get(),
                submodule=self.submodule_entry.get()
            )
            CommitListWindow(self, commits)
        except Exception as e:
            self._log_error(str(e))

    def _search_commits_by_text(self):
        """Handle commits search by text"""
        try:
            if not self._validate_inputs():
                return

            self.version_finder.update_repository(branch=self.branch_entry.get())
            commits = self.version_finder.find_commits_by_text(
                self.search_text_pattern_entry.get(),
                submodule=self.submodule_entry.get()
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

    def _log_error(self, message: str):
        """Log error message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"❌ Error: {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def _setup_icon(self):
        """Setup application icon"""
        try:
            with importlib.resources.path("version_finder_gui.assets", 'icon.png') as icon_path:
                self.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except Exception:
            pass

    def center_window(self):
        """Center the window on the screen"""
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")


def launch_gui():
    print("lunching GUI")
    app = VersionFinderGUI()
    app.mainloop()


launch_gui()
