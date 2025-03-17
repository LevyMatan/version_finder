import customtkinter as ctk
import argparse
from pathlib import Path
from enum import Enum, auto
import tkinter as tk
from typing import List, Tuple
from tkinter import filedialog, messagebox
import importlib.resources
import multiprocessing
import queue
from version_finder.version_finder import VersionFinder
from version_finder.common import parse_arguments
from version_finder.logger import get_logger, configure_logging
from version_finder_gui.widgets import AutocompleteEntry, CommitListWindow, center_window, LoadingSpinner
import time
import os
from PIL import Image

logger = get_logger(__name__)
# Define message types for inter-process communication


class MessageType(Enum):
    TASK_REQUEST = auto()
    TASK_RESULT = auto()
    TASK_ERROR = auto()
    SHUTDOWN = auto()


class VersionFinderTasks(Enum):
    FIND_VERSION = auto()
    COMMITS_BETWEEN_VERSIONS = auto()
    COMMITS_BY_TEXT = auto()

# Worker process function


def version_finder_worker(request_queue, response_queue, exit_event=None):
    """Worker process for version finder operations"""
    logger.info("Worker process started")

    version_finder = None
    waiting_for_confirmation = False
    pending_init_task_id = None

    while True:
        try:
            # Check for exit signal
            if exit_event and exit_event.is_set():
                logger.info("Exit event received, shutting down worker")
                break

            # Get next task from queue with timeout
            try:
                message = request_queue.get(timeout=0.5)  # 500ms timeout
            except queue.Empty:
                continue

            # Handle shutdown message
            if message["type"] == MessageType.SHUTDOWN:
                logger.info("Shutdown message received")
                break

            # Extract task info
            task = message.get("task")
            task_id = message.get("task_id")
            args = message.get("args", {})

            # Handle user confirmation for repository initialization
            if task == "confirm_init":
                if waiting_for_confirmation and pending_init_task_id:
                    logger.info("Received confirmation for repository initialization")
                    # Re-initialize with force=True
                    version_finder = VersionFinder(args["repo_path"], force=True)
                    waiting_for_confirmation = False

                    # Send success response for the original init task
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": "init_repo_confirmed",
                        "result": {
                            "status": "success",
                            "original_task_id": pending_init_task_id
                        }
                    })
                    pending_init_task_id = None
                continue

            # Process tasks
            try:
                # Initialize version finder if needed
                if task == "init_repo":
                    repo_path = args["repo_path"]
                    user_confirmation = args.get("user_confirmation", False)
                    logger.info(f"Initializing version finder with repo: {repo_path}, force: {user_confirmation}")

                    try:
                        # Initialize version finder with specified force parameter
                        version_finder = VersionFinder(repo_path, force=user_confirmation)

                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": {"status": "success"}
                        })
                    except Exception as e:
                        # Handle other initialization errors
                        response_queue.put({
                            "type": MessageType.TASK_ERROR,
                            "task_id": task_id,
                            "error": str(e),
                            "error_type": type(e).__name__
                        })
                elif task == "update_repository":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.update_repository(**args)
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "get_branches":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.list_branches(), version_finder.updated_branch
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "get_submodules":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.list_submodules()
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "find_version":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.find_version(**args)
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "find_all_commits_between_versions":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.find_commits_between_versions(**args)
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "find_commit_by_text":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    result = version_finder.find_commits_by_text(**args)
                    response_queue.put({
                        "type": MessageType.TASK_RESULT,
                        "task_id": task_id,
                        "result": result
                    })
                elif task == "restore_state":
                    if not version_finder:
                        raise ValueError("Version finder not initialized")
                    # Explicitly restore repository state
                    if version_finder.has_saved_state():
                        logger.info("Explicitly restoring repository state on close")
                        result = version_finder.restore_repository_state()
                        # Set flag to prevent destructor from trying to restore again
                        version_finder._state_restored = True

                        # Force the destructor to be called by deleting the reference
                        logger.info("Forcing VersionFinder destructor by deleting reference")
                        version_finder_copy = version_finder
                        version_finder = None
                        del version_finder_copy

                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": {"status": "success", "restored": result, "forced_destructor": True}
                        })
                    else:
                        logger.info("No saved state to restore")
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": {"status": "success", "restored": False}
                        })
                else:
                    raise ValueError(f"Unknown task: {task}")
            except Exception as e:
                # Get full traceback for better debugging
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Error executing task {task}: {str(e)}\n{error_traceback}")

                # Send error back
                response_queue.put({
                    "type": MessageType.TASK_ERROR,
                    "task_id": task_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "traceback": error_traceback
                })
        except Exception as e:
            # Get full traceback for better debugging
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Unexpected error in worker process: {str(e)}\n{error_traceback}")

            # Send error back to main process
            response_queue.put({
                "type": MessageType.TASK_ERROR,
                "task_id": None,  # No specific task ID
                "error": f"Unexpected worker error: {str(e)}",
                "error_type": type(e).__name__,
                "traceback": error_traceback
            })

    logger.info("Worker process terminated")


ctk.set_default_color_theme("green")


class VersionFinderGUI(ctk.CTk):
    def __init__(self, path: str = ''):
        super().__init__()
        self.repo_path = Path(path).resolve() if path else path
        self.title("Version Finder")
        self.version_finder: VersionFinder = None
        self.selected_branch: str = ''
        self.selected_submodule: str = ''

        # Setup multiprocessing
        self.worker_process = None
        self.request_queue = None
        self.response_queue = None
        self.task_callbacks = {}
        self.next_task_id = 0
        self.waiting_for_confirmation = False

        # Initialize UI
        self._setup_window()
        self._create_window_layout()
        self._setup_icon()
        self._show_find_version()

        # Center window on screen
        center_window(self)

        # Focus on window
        self.focus_force()

        # Start checking for worker responses
        self.after(100, self._check_worker_responses)

        # If path is provided, update the entry field and initialize
        if self.repo_path:
            # Update the entry field after UI is created
            self.after(100, lambda: self._update_repo_path_entry())

    def _update_repo_path_entry(self):
        """Update the repository path entry field with the current path"""
        if hasattr(self, 'dir_entry') and self.repo_path:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, str(self.repo_path))
            self._initialize_version_finder()

    def _start_worker_process(self):
        """Start the worker process for background operations"""
        if self.worker_process is not None and self.worker_process.is_alive():
            return

        self.request_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        self.exit_event = multiprocessing.Event()
        self.worker_process = multiprocessing.Process(
            target=version_finder_worker,
            args=(self.request_queue, self.response_queue, self.exit_event),
            daemon=False  # Use non-daemon process for proper cleanup
        )
        self.worker_process.start()
        logger.info(f"Started worker process with PID: {self.worker_process.pid}")

    def _stop_worker_process(self):
        """Stop the worker process"""
        if self.worker_process is not None and self.worker_process.is_alive():
            try:
                # First try to signal exit via event
                logger.info("Setting exit event for worker process")
                self.exit_event.set()

                # Give the process a moment to shut down gracefully
                self.worker_process.join(timeout=2)

                # If still alive, try shutdown message
                if self.worker_process.is_alive():
                    logger.info("Worker still alive, sending shutdown message")
                    self.request_queue.put({"type": MessageType.SHUTDOWN})
                    self.worker_process.join(timeout=2)

                # If still alive, terminate
                if self.worker_process.is_alive():
                    logger.warning("Worker process did not exit, terminating forcefully")
                    self.worker_process.terminate()
                else:
                    logger.info("Worker process shut down gracefully")
            except Exception as e:
                logger.error(f"Error stopping worker process: {str(e)}")

    def _check_worker_responses(self):
        """Check for responses from the worker process"""
        if self.response_queue is not None:
            try:
                # Non-blocking check for messages
                while True:
                    try:
                        message = self.response_queue.get_nowait()
                        self._handle_worker_message(message)
                    except queue.Empty:
                        break

                # Check for timed-out tasks
                self._check_task_timeouts()

            except Exception as e:
                logger.error(f"Error checking worker responses: {str(e)}")

        # Schedule the next check
        self.after(100, self._check_worker_responses)

    def _check_task_timeouts(self):
        """Check for tasks that have timed out"""
        current_time = time.time()
        timed_out_tasks = []

        # Find timed-out tasks
        for task_id, callback_info in self.task_callbacks.items():
            start_time = callback_info.get("start_time", 0)
            timeout = callback_info.get("timeout", 30)

            if current_time - start_time > timeout:
                timed_out_tasks.append(task_id)

        # Handle timed-out tasks
        for task_id in timed_out_tasks:
            callback_info = self.task_callbacks.pop(task_id)
            callback = callback_info["callback"]
            spinner = callback_info.get("spinner")

            # Stop the spinner
            if spinner is not None:
                spinner.stop()

            # Log timeout error
            error_msg = f"Task timed out after {callback_info.get('timeout', 30)} seconds"
            logger.error(f"Task timeout: {error_msg}")

            # Display error in UI
            self._log_error(f"Timeout: {error_msg}")

            # Call callback with error
            if callback is not None:
                callback(None, error=error_msg)

    def _handle_worker_message(self, message):
        """Handle a message from the worker process"""
        message_type = message["type"]
        task_id = message.get("task_id")

        # Handle initial repository state message
        if message_type == MessageType.TASK_RESULT and task_id == "initial_state":
            self._handle_initial_repo_state(message["result"])
            return

        # Handle repository initialization confirmation
        if message_type == MessageType.TASK_RESULT and task_id == "init_repo_confirmed":
            self._log_output("Repository initialization confirmed")

            # Check if we have the original task ID
            original_task_id = message.get("result", {}).get("original_task_id")

            if original_task_id is not None and original_task_id in self.task_callbacks:
                # Get the callback info for the original task
                callback_info = self.task_callbacks.pop(original_task_id)
                callback = callback_info.get("callback")
                spinner = callback_info.get("spinner")

                # Stop the spinner if it exists
                if spinner:
                    spinner.stop()

                # Call the callback with the success result
                if callback:
                    callback(message["result"])
                    return
            else:
                # Find and remove any pending init_repo tasks from the callbacks
                # to prevent timeout errors for the original task
                for task_id, callback_info in list(self.task_callbacks.items()):
                    if callback_info.get("task_name") == "init_repo":
                        # Get the callback and remove the task
                        callback = callback_info.get("callback")
                        spinner = callback_info.get("spinner")
                        self.task_callbacks.pop(task_id)

                        # Stop the spinner if it exists
                        if spinner:
                            spinner.stop()

                        # Call the callback with the success result
                        if callback:
                            callback(message["result"])
                            return

            # If no pending init_repo task was found, just call the handler directly
            self._on_repo_initialized(message["result"])
            return

        # Handle general worker errors (no specific task ID)
        if message_type == MessageType.TASK_ERROR and task_id is None:
            error_msg = message.get("error", "Unknown error")
            error_type = message.get("error_type", "Error")

            # Log the error
            logger.error(f"Worker error ({error_type}): {error_msg}")

            # Display error in UI
            self._log_error(f"{error_type}: {error_msg}")

            # Show error dialog
            messagebox.showerror("Worker Error", f"{error_type}: {error_msg}")

            # Stop all active spinners
            self._stop_all_spinners()
            return

        # Handle task-specific messages
        if task_id in self.task_callbacks:
            callback_info = self.task_callbacks.pop(task_id)
            callback = callback_info["callback"]
            spinner = callback_info.get("spinner")

            # Stop the spinner if one was created
            if spinner is not None:
                spinner.stop()

            if message_type == MessageType.TASK_RESULT:
                callback(message["result"])
            elif message_type == MessageType.TASK_ERROR:
                error_msg = message["error"]
                error_type = message["error_type"]
                logger.error(f"Task error ({error_type}): {error_msg}")

                # Handle pending confirmation errors differently
                if error_type == "PendingConfirmation":
                    self._log_warning(error_msg)
                    # Don't show error dialog for pending confirmation
                else:
                    # Display error in UI
                    self._log_error(f"{error_type}: {error_msg}")

                    # Show error dialog
                    messagebox.showerror("Error", f"{error_type}: {error_msg}")

                # Call callback with error
                callback(None, error=error_msg)
        elif message_type == MessageType.TASK_ERROR:
            # Handle error for unknown task ID
            error_msg = message.get("error", "Unknown error")
            error_type = message.get("error_type", "Error")

            # Log the error
            logger.error(f"Task error for unknown task ({error_type}): {error_msg}")

            # Display error in UI
            self._log_error(f"{error_type}: {error_msg}")

            # Show error dialog
            messagebox.showerror("Error", f"{error_type}: {error_msg}")

            # Stop all active spinners as a precaution
            self._stop_all_spinners()

    def _handle_initial_repo_state(self, state):
        """Handle the initial repository state message"""
        branch = state.get("branch")
        has_changes = state.get("has_changes", False)
        has_submodules = bool(state.get("submodules", {}))

        if branch:
            if branch.startswith("HEAD:"):
                commit = branch.split(":", 1)[1][:8]  # Show first 8 chars of commit hash
                self._log_output(f"Repository is in detached HEAD state at commit {commit}")
            else:
                self._log_output(f"Repository is on branch: {branch}")

        if has_changes:
            self._log_warning("Repository has uncommitted changes")
            self._log_output("Waiting for user confirmation before proceeding...")

            # Stop any existing spinners since we're waiting for user input
            self._stop_all_spinners()

            # Set flag to indicate we're waiting for confirmation
            self.waiting_for_confirmation = True

            # Build message with details about what will happen
            message = (
                "The repository has uncommitted changes. Version Finder will:\n\n"
                "1. Stash your changes with a unique identifier\n"
                "2. Perform the requested operations\n"
                "3. Restore your original branch and stashed changes when closing\n"
            )

            if has_submodules:
                message += "\nSubmodules with uncommitted changes will also be handled similarly."

            message += "\n\nDo you want to proceed?"

            # Ask user if they want to proceed
            proceed = messagebox.askyesno(
                "Uncommitted Changes",
                message,
                icon="warning"
            )

            # Reset flag
            self.waiting_for_confirmation = False

            if proceed:
                # Send confirmation to worker
                self._execute_task(
                    "confirm_init",
                    args={"repo_path": str(self.repo_path), "proceed": True},
                    callback=None  # No callback needed as worker will send init_repo_confirmed
                )
            else:
                self._log_output("Operation cancelled by user")
                # Clear repository path
                self.dir_entry.delete(0, "end")
                self.repo_path = ""

        # Save initial state for reference
        self.initial_repo_state = state

    def _log_warning(self, message: str):
        """Log warning message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"⚠️ Warning: {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
        logger.warning(message)

    def _stop_all_spinners(self):
        """Stop all active spinners"""
        # Stop all spinners in task_callbacks
        for task_id, callback_info in list(self.task_callbacks.items()):
            spinner = callback_info.get("spinner")
            if spinner is not None:
                spinner.stop()

        # Clear task callbacks since we've handled all pending tasks
        self.task_callbacks.clear()

    def _execute_task(
            self,
            task_name,
            args=None,
            callback=None,
            show_spinner=True,
            spinner_parent=None,
            spinner_text="Processing...",
            timeout=30):
        """Execute a task in the worker process"""
        if self.worker_process is None or not self.worker_process.is_alive():
            self._start_worker_process()

        # Don't execute new tasks if waiting for confirmation
        if self.waiting_for_confirmation and task_name != "confirm_proceed":
            logger.warning(f"Task {task_name} not executed - waiting for user confirmation")
            if callback:
                callback(None, error="Operation pending user confirmation")
            return None

        task_id = self.next_task_id
        self.next_task_id += 1

        # Create a spinner if requested
        spinner = None
        if show_spinner and spinner_parent is not None:
            spinner = LoadingSpinner(spinner_parent, text=spinner_text)
            spinner.start()

        # Store callback with task ID
        if callback is not None:
            self.task_callbacks[task_id] = {
                "callback": callback,
                "spinner": spinner,
                "start_time": time.time(),
                "timeout": timeout,
                "task_name": task_name  # Store the task name for reference
            }

        # Send task to worker
        self.request_queue.put({
            "type": MessageType.TASK_REQUEST,
            "task": task_name,
            "args": args or {},
            "task_id": task_id
        })

        return task_id

    def _setup_window(self):
        """Configure the main window settings"""
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Handle window close event"""
        # Explicitly restore repository state before shutting down
        if self.worker_process is not None and self.worker_process.is_alive():
            try:
                # Log that we're closing
                logger.info("Application closing, restoring repository state...")
                self._log_output("Closing application, restoring repository state...")

                # First try to signal exit via event
                logger.info("Setting exit event for worker process")
                self.exit_event.set()

                # Explicitly request state restoration
                try:
                    # Send a task to explicitly restore state and delete the version_finder
                    self._execute_task(
                        "restore_state", callback=lambda result, error=None: logger.info(
                            f"State restoration result: {result}, error: {error}"), timeout=5)
                    # Give a moment for the task to complete
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error during explicit state restoration: {str(e)}")

                # Wait for the worker to finish (with timeout)
                self.worker_process.join(timeout=3)

                # If still alive, try shutdown message
                if self.worker_process.is_alive():
                    logger.info("Worker still alive, sending shutdown message")
                    self.request_queue.put({"type": MessageType.SHUTDOWN})
                    self.worker_process.join(timeout=2)

                # If still alive, terminate
                if self.worker_process.is_alive():
                    logger.warning("Worker process did not exit, terminating forcefully")
                    self.worker_process.terminate()
                else:
                    logger.info("Worker process shut down gracefully")

            except Exception as e:
                logger.error(f"Error during shutdown: {str(e)}")

        # Now destroy the window
        self.destroy()

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
        """Handle branch selection"""
        if not branch:
            return

        if branch != self.selected_branch:
            self.selected_branch = branch
            self._update_repository()

    def _on_submodule_select(self, submodule: str):
        """Handle submodule selection"""
        self.selected_submodule = submodule

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
            submodule_frame, width=400, placeholder_text="Select a submodule [Optional]")
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
            command=self._on_close,
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
        directory = filedialog.askdirectory(initialdir=Path.cwd())
        if directory:
            # Stop any existing worker process
            self._stop_worker_process()

            # Update repository path
            self.repo_path = Path(directory).resolve()

            # Update directory entry
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, str(self.repo_path))

            # Clear branch and submodule selections
            self.selected_branch = ""
            self.selected_submodule = ""

            # Initialize with new repository
            self._initialize_version_finder()

            self._log_output(f"Selected repository: {self.repo_path}")
        else:
            self._log_output("No directory selected")

    def _initialize_version_finder(self):
        """Initialize the VersionFinder with the selected repository path"""
        try:
            # Initialize with user_confirmation=False first
            self._execute_task(
                "init_repo",
                args={"repo_path": str(self.repo_path), "user_confirmation": False},
                callback=self._handle_init_result,
                spinner_parent=self.main_frame,
                spinner_text="Initializing repository..."
            )
        except Exception as e:
            logger.error(f"Error initializing VersionFinder: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize repository: {str(e)}")

    def _handle_init_result(self, result, error=None):
        """Handle the result of repository initialization"""
        if error:
            # Check if error is due to uncommitted changes
            if "Repository has uncommitted changes" in str(error):
                message = (
                    "The repository has uncommitted changes. Version Finder will:\n\n"
                    "1. Stash your changes with a unique identifier\n"
                    "2. Perform the requested operations\n"
                    "3. Restore your original branch and stashed changes when closing\n\n"
                    "Do you want to proceed?"
                )
                if messagebox.askyesno("Uncommitted Changes", message, icon="warning"):
                    # Retry initialization with user_confirmation=True
                    self._execute_task(
                        "init_repo",
                        args={"repo_path": str(self.repo_path), "user_confirmation": True},
                        callback=self._on_repo_initialized,
                        spinner_parent=self.main_frame,
                        spinner_text="Initializing repository..."
                    )
                else:
                    self._log_output("Operation cancelled by user")
                    # Clear repository path
                    self.dir_entry.delete(0, "end")
                    self.repo_path = ""
                return
            else:
                self._log_error(f"Error initializing repository: {error}")
                return

        self._on_repo_initialized(result)

    def _handle_branches_loaded(self, branches: Tuple[List[str], str], error=None):
        """Handle branches loaded from worker process"""
        branches, current_branch = branches
        if error:
            self._log_error(f"Error loading branches: {error}")
            return

        if not branches:
            self._log_warning("No branches found in repository")
            return

        # Update branch autocomplete entry
        self.branch_entry.configure(state="normal")
        self.branch_entry.suggestions = branches

        # Set the current branch as the first suggestion
        self.branch_entry.insert(0, current_branch)
        self._log_output(f"Loaded {len(branches)} branches")

        # Set the selected branch
        self.selected_branch = current_branch

        # Update repository with selected branch
        self._update_repository()

    def _update_repository(self):
        """Update the repository with the selected branch"""
        if not self.selected_branch:
            return

        self._execute_task(
            "update_repository",
            args={"branch": self.selected_branch},
            callback=self._handle_repository_updated,
            spinner_parent=self.main_content_frame,
            spinner_text=f"Updating to branch {self.selected_branch}..."
        )

    def _handle_repository_updated(self, result, error=None):
        """Handle repository update result"""
        if error:
            logger.error(f"Error updating repository: {error}")
            messagebox.showerror("Error", f"Failed to update repository: {error}")
            return

        # Get submodules
        self._execute_task(
            "get_submodules",
            callback=self._handle_submodules_loaded,
            spinner_parent=self.main_content_frame,
            spinner_text="Loading submodules..."
        )

    def _handle_submodules_loaded(self, submodules: List[str], error=None):
        """Handle submodules loaded from worker process"""
        if error:
            return
        self.submodule_entry.configure(state="normal")

        # Clear submodule entry
        self.submodule_entry.delete(0, "end")
        self.submodule_entry.suggestions = submodules

        # Update submodule entry
        if submodules:
            self.submodule_entry.insert(0, "Select a submodule [Optional]")
            self._log_output("Loaded submodules successfully.")
        else:
            self.submodule_entry.insert(0, f"No submodules found (on branch: {self.selected_branch})")
            self._log_output(
                f"There are no submodules in the repository (with selected branch: "
                f"{self.selected_branch}).")
            self.submodule_entry.configure(state="disabled")
            self.submodule_entry.configure(text_color="gray")

        # Enable UI elements now that repository is ready
        self._enable_ui_after_repo_load()

    def ensure_version_finder_initialized(func):
        def wrapper(self, *args, **kwargs):
            if self.version_finder is None:
                self._log_error("Repository not initialized")
                messagebox.showerror("Error", "Repository not initialized. Please select a repository first.")
                return None
            return func(self, *args, **kwargs)
        return wrapper

    @ensure_version_finder_initialized
    def _find_version(self):
        """Find version for the given commit"""
        commit_sha = self.commit_entry.get().strip()
        if not commit_sha:
            messagebox.showwarning("Input Error", "Please enter a commit SHA")
            return

        # Get current submodule selection
        submodule = self.selected_submodule if self.selected_submodule else None

        # Execute the task in the worker process
        self._execute_task(
            "find_version",
            args={
                "commit_sha": commit_sha,
                "submodule": submodule
            },
            callback=self._handle_find_version_result,
            spinner_parent=self.main_content_frame,
            spinner_text=f"Finding version for commit {commit_sha[:7]}..."
        )

    def _handle_find_version_result(self, result, error=None):
        """Handle the result of find_version task"""
        if error:
            self._log_error(f"Error finding version: {error}")
            return

        if not result:
            self._log_error("No version found for this commit")
            return

        # Display the result
        self._log_output(f"Version found: {result}")

        # Update the result label
        if hasattr(self, 'version_result_label'):
            self.version_result_label.configure(text=f"Version: {result}")

    def _find_all_commits_between_versions(self):
        """Find all commits between two versions"""
        from_version = self.start_version_entry.get().strip()
        to_version = self.end_version_entry.get().strip()

        if not from_version or not to_version:
            messagebox.showwarning("Input Error", "Please enter both from and to versions")
            return

        # Get current submodule selection
        submodule = self.selected_submodule if self.selected_submodule else None

        # Execute the task in the worker process
        self._execute_task(
            "find_all_commits_between_versions",
            args={
                "from_version": from_version,
                "to_version": to_version,
                "submodule": submodule
            },
            callback=self._handle_commits_between_versions_result,
            spinner_parent=self.commits_result_frame,
            spinner_text=f"Finding commits between {from_version} and {to_version}..."
        )

    def _handle_commits_between_versions_result(self, commits, error=None):
        """Handle the result of find_all_commits_between_versions task"""
        if error:
            self._log_error(f"Error finding commits: {error}")
            return

        if not commits:
            self._log_output("No commits found between these versions")
            return

        # Log the number of commits found
        self._log_output(f"Found {len(commits)} commits between versions")

        # Display commits in a new window
        CommitListWindow(self, "Commits Between Versions", commits)

    def _find_commit_by_text(self):
        """Find commits containing specific text"""
        search_text = self.search_text_pattern_entry.get().strip()

        if not search_text:
            messagebox.showwarning("Input Error", "Please enter search text")
            return

        # Get current submodule selection
        submodule = self.selected_submodule if self.selected_submodule else None

        # Execute the task in the worker process
        self._execute_task(
            "find_commit_by_text",
            args={
                "text": search_text,
                "submodule": submodule
            },
            callback=self._handle_find_commit_by_text_result,
            spinner_parent=self.main_content_frame,
            spinner_text=f"Searching for commits with text: {search_text}..."
        )

    def _handle_find_commit_by_text_result(self, commits, error=None):
        """Handle the result of find_commit_by_text task"""
        if error:
            self._log_error(f"Error searching commits: {error}")
            return

        if not commits:
            self._log_output("No commits found matching the search text")
            return

        # Log the number of commits found
        self._log_output(f"Found {len(commits)} commits matching the search")

        # Display commits in a new window
        CommitListWindow(self, "Search Results", commits)

    def _search(self):
        """Handle version search"""
        try:
            if not self._validate_inputs():
                return
            if (self.current_displayed_task == VersionFinderTasks.FIND_VERSION):
                self._find_version()
            elif (self.current_displayed_task == VersionFinderTasks.COMMITS_BETWEEN_VERSIONS):
                self._find_all_commits_between_versions()
            elif (self.current_displayed_task == VersionFinderTasks.COMMITS_BY_TEXT):
                self._find_commit_by_text()
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

        # Check if repository is initialized
        if self.version_finder is None:
            self._log_warning("Repository not initialized, attempting to initialize now")
            self._initialize_version_finder()
            # Return False to prevent proceeding until initialization is complete
            return False

        # If we have a selected branch but repo is not task ready, update it first
        if self.selected_branch:
            self._execute_task(
                "update_repository",
                args={"branch": self.selected_branch},
                callback=lambda result, error=None: self._handle_update_before_search(result, error),
                spinner_parent=self.main_content_frame,
                spinner_text=f"Updating to branch {self.selected_branch}..."
            )
            return False  # Return False to prevent proceeding until update is complete

        return True

    def _handle_update_before_search(self, result, error=None):
        """Handle repository update result and proceed with search if successful"""
        if error:
            logger.error(f"Error updating repository: {error}")
            messagebox.showerror("Error", f"Failed to update repository: {error}")
            return

        # Now proceed with the search
        if self.current_displayed_task == VersionFinderTasks.FIND_VERSION:
            self._find_version()
        elif self.current_displayed_task == VersionFinderTasks.COMMITS_BETWEEN_VERSIONS:
            self._find_all_commits_between_versions()
        elif self.current_displayed_task == VersionFinderTasks.COMMITS_BY_TEXT:
            self._find_commit_by_text()

    def _log_output(self, message: str):
        """Log output message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"✅ {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
        logger.debug(message)

    def _log_error(self, message: str):
        """Log error message to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"❌ Error: {message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
        logger.error(message)

    def _setup_icon(self):
        """Setup application icon"""
        try:
            with importlib.resources.path("version_finder_gui.assets", 'icon.png') as icon_path:
                if os.name == 'nt':  # Windows
                    # Convert PNG to ICO using PIL
                    icon = Image.open(str(icon_path))
                    icon_path_ico = str(icon_path).replace('.png', '.ico')
                    icon.save(icon_path_ico, format='ICO')
                    # Set both window and taskbar icons
                    self.iconbitmap(icon_path_ico)
                    self.wm_iconbitmap(icon_path_ico)
                    # Clean up temporary .ico file
                    os.remove(icon_path_ico)
                else:  # Unix-like systems
                    self.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except Exception as e:
            logger.warning(f"Failed to set application icon: {e}")
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

    def _enable_ui_after_repo_load(self):
        """Enable UI elements after repository is loaded"""
        # Enable search button and other UI elements
        for widget in self.task_frame.winfo_children():
            if isinstance(widget, ctk.CTkEntry) or isinstance(widget, ctk.CTkButton):
                widget.configure(state="normal")

        self._log_output("Repository ready for operations")

    def init_repo(self, repo_path):
        """Initialize the repository"""
        self.repo_path = repo_path
        self._log_output(f"Initializing repository: {repo_path}")

        # Start worker process if not already running
        if not self.worker_process or not self.worker_process.is_alive():
            self.request_queue = multiprocessing.Queue()
            self.response_queue = multiprocessing.Queue()
            self.exit_event = multiprocessing.Event()

            self.worker_process = multiprocessing.Process(
                target=version_finder_worker,
                args=(self.request_queue, self.response_queue, self.exit_event),
                daemon=False  # Use non-daemon process for proper cleanup
            )
            self.worker_process.start()

            # Start response checker
            self.after(100, self._check_worker_responses)

        # Send init_repo task to worker
        self._execute_task(
            "init_repo",
            args={"repo_path": repo_path},
            callback=self._on_repo_initialized,
            show_spinner=True,
            spinner_parent=self.main_frame,
            spinner_text="Initializing repository..."
        )

    def _on_repo_initialized(self, result, error=None):
        """Handle repository initialization result"""
        if error:
            logger.error(f"Error initializing repository: {error}")
            messagebox.showerror("Error", f"Failed to initialize repository: {error}")
            return

        # Set version_finder to a non-None value to indicate repository is initialized
        # This is a placeholder since the actual VersionFinder object is in the worker process
        self.version_finder = True

        # Get branches
        self._execute_task(
            "get_branches",
            callback=self._handle_branches_loaded,
            spinner_parent=self.main_content_frame,
            spinner_text="Loading branches..."
        )


def gui_main(args: argparse.Namespace) -> int:
    if args.version:
        from version_finder_gui.__version__ import __version__
        print(f"version_finder gui-v{__version__}")
        return 0

    configure_logging(verbose=args.verbose)
    app = VersionFinderGUI(args.path)
    app.mainloop()
    return 0


def main():
    args = parse_arguments()
    gui_main(args)


if __name__ == "__main__":
    main()
