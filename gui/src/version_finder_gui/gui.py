import customtkinter as ctk
import argparse
from pathlib import Path
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.resources
import multiprocessing
import queue
from version_finder.version_finder import VersionFinder, Commit
from version_finder.common import parse_arguments
from version_finder.logger import get_logger, configure_logging
from version_finder_gui.widgets import AutocompleteEntry, CommitListWindow, center_window, LoadingSpinner
import time
import subprocess
import os

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
    
    # Initialize version finder
    version_finder = None
    waiting_for_confirmation = False
    pending_init_task_id = None  # Track the ID of the pending init task
    
    # Process tasks until shutdown
    while True:
        try:
            # Check if exit event is set
            if exit_event and exit_event.is_set():
                logger.info("Worker process detected exit event")
                # Restore original branch if needed
                if version_finder and version_finder.has_saved_state():
                    try:
                        logger.info("Restoring original repository state due to exit event")
                        version_finder.restore_repository_state()
                        # Set flag to prevent destructor from trying to restore again
                        version_finder._state_restored = True
                    except Exception as e:
                        logger.error(f"Failed to restore original repository state: {str(e)}")
                break
            
            # Get the next task from the queue with timeout
            try:
                request = request_queue.get(timeout=0.5)
            except queue.Empty:
                continue
                
            # Check if we should shut down
            if request["type"] == MessageType.SHUTDOWN:
                logger.info("Worker process shutting down")
                
                # Restore original branch if needed
                # Note: We're explicitly restoring here for better control and logging
                # The VersionFinder.__del__ method will also try to restore as a safety net
                if version_finder and version_finder.has_saved_state():
                    try:
                        logger.info("Restoring original repository state")
                        # Get the state before restoration for logging
                        state = version_finder.get_saved_state()
                        has_changes = state.get("has_changes", False)
                        stash_created = state.get("stash_created", False)
                        
                        if has_changes:
                            if stash_created:
                                logger.info("Attempting to restore stashed changes")
                            else:
                                logger.warning("Repository had changes but they were not stashed")
                        
                        # Perform the restoration
                        if version_finder.restore_repository_state():
                            logger.info("Original repository state restored successfully")
                            
                            # Verify the restoration
                            current_branch = version_finder.get_current_branch()
                            original_branch = state.get("branch")
                            if original_branch and current_branch:
                                if original_branch.startswith("HEAD:"):
                                    logger.info(f"Restored to detached HEAD state")
                                else:
                                    logger.info(f"Restored to branch: {current_branch}")
                            
                            # Check if we still have uncommitted changes
                            if has_changes and version_finder.has_uncommitted_changes():
                                logger.info("Uncommitted changes were successfully restored")
                            elif has_changes and not version_finder.has_uncommitted_changes():
                                logger.error("Failed to restore uncommitted changes")
                            
                            # Set a flag to indicate we've already restored the state
                            # This will prevent the destructor from trying to restore again
                            version_finder._state_restored = True
                        else:
                            logger.error("Failed to restore original repository state")
                    except Exception as e:
                        logger.error(f"Failed to restore original repository state: {str(e)}")
                        # Get full traceback for better debugging
                        import traceback
                        error_traceback = traceback.format_exc()
                        logger.error(f"Restoration error details: {error_traceback}")
                
                break
                
            # Process the task
            if request["type"] == MessageType.TASK_REQUEST:
                task = request["task"]
                task_id = request.get("task_id")
                args = request.get("args", {})
                
                # Handle confirmation response
                if task == "confirm_proceed":
                    user_confirmed_proceed = args.get("proceed", False)
                    logger.info(f"User confirmed proceed: {user_confirmed_proceed}")
                    waiting_for_confirmation = False
                    
                    # Send confirmation to version finder
                    if not user_confirmed_proceed:
                        # If user didn't confirm, we'll shut down
                        logger.info("User cancelled operation due to uncommitted changes")
                        response_queue.put({
                            "type": MessageType.TASK_ERROR,
                            "task_id": None,
                            "error": "Operation cancelled by user due to uncommitted changes",
                            "error_type": "UserCancelled"
                        })
                    else:
                        # User confirmed, send success response for the init_repo task
                        # We don't have the task_id, but we can send a success response with a special task_id
                        logger.info("User confirmed to proceed with uncommitted changes")
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": "init_repo_confirmed",
                            "result": {"status": "success", "original_task_id": pending_init_task_id}
                        })
                    continue
                
                # If waiting for confirmation, don't process other tasks
                if waiting_for_confirmation and task != "confirm_proceed":
                    logger.warning(f"Task {task} not processed - waiting for user confirmation")
                    response_queue.put({
                        "type": MessageType.TASK_ERROR,
                        "task_id": task_id,
                        "error": "Operation pending user confirmation",
                        "error_type": "PendingConfirmation"
                    })
                    continue
                
                try:
                    # Initialize version finder if needed
                    if task == "init_repo" and version_finder is None:
                        repo_path = args["repo_path"]
                        logger.info(f"Initializing version finder with repo: {repo_path}")
                        
                        # Store the task ID in case we need to wait for confirmation
                        pending_init_task_id = task_id
                        
                        # Check if repo exists
                        if not os.path.exists(repo_path):
                            raise ValueError(f"Repository path does not exist: {repo_path}")
                        
                        # Initialize version finder with force=True to allow uncommitted changes
                        version_finder = VersionFinder(repo_path, force=True)
                        
                        # Check repository state
                        state = version_finder.get_saved_state()
                        logger.info(f"Repository state: {state}")
                        
                        # Send initial state to main process
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": "initial_state",
                            "result": state
                        })
                        
                        # If there are uncommitted changes, wait for user confirmation
                        if state.get("has_changes", False):
                            logger.info("Repository has uncommitted changes, waiting for user confirmation")
                            # Don't send success response yet - wait for confirmation
                            # We'll send the success response after receiving the confirmation
                            waiting_for_confirmation = True
                            continue
                        
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": {"status": "success"}
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
                        result = version_finder.get_branches()
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": result
                        })
                    elif task == "get_submodules":
                        if not version_finder:
                            raise ValueError("Version finder not initialized")
                        result = version_finder.get_submodules()
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
                        result = version_finder.find_all_commits_between_versions(**args)
                        response_queue.put({
                            "type": MessageType.TASK_RESULT,
                            "task_id": task_id,
                            "result": result
                        })
                    elif task == "find_commit_by_text":
                        if not version_finder:
                            raise ValueError("Version finder not initialized")
                        result = version_finder.find_commit_by_text(**args)
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
            
            # Send confirmation to worker
            self.request_queue.put({
                "type": MessageType.TASK_REQUEST,
                "task": "confirm_proceed",
                "args": {"proceed": proceed}
            })
            
            if not proceed:
                self._log_warning("Operation cancelled by user")
                self._stop_worker_process()
                return
            else:
                self._log_output("Proceeding with operations...")
                
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
  
    def _execute_task(self, task_name, args=None, callback=None, show_spinner=True, spinner_parent=None, spinner_text="Processing...", timeout=30):
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
                        "restore_state",
                        callback=lambda result, error=None: logger.info(f"State restoration result: {result}, error: {error}"),
                        timeout=5
                    )
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
        """Handle branch selection"""
        if not branch:
            return
            
        self.selected_branch = branch
        self._update_repository()
        
    def _on_submodule_select(self, submodule):
        """Handle submodule selection"""
        self.selected_submodule = submodule
        
    def _create_branch_selection(self, parent_frame):
        """Create the branch selection section"""
        branch_frame = ctk.CTkFrame(parent_frame)
        branch_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(branch_frame, text="Branch:").grid(row=0, column=0, padx=5)
        
        # Create branch dropdown instead of autocomplete entry
        self.branch_var = ctk.StringVar()
        self.branch_dropdown = ctk.CTkOptionMenu(
            branch_frame, 
            variable=self.branch_var,
            values=[],
            command=self._on_branch_select,
            width=400,
            dynamic_resizing=False
        )
        self.branch_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        return branch_frame

    def _create_submodule_selection(self, parent_frame):
        """Create the submodule selection section"""
        submodule_frame = ctk.CTkFrame(parent_frame)
        submodule_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(submodule_frame, text="Submodule:").grid(row=0, column=0, padx=5)
        
        # Create submodule dropdown instead of autocomplete entry
        self.submodule_var = ctk.StringVar()
        self.submodule_dropdown = ctk.CTkOptionMenu(
            submodule_frame, 
            variable=self.submodule_var,
            values=[""],
            command=self._on_submodule_select,
            width=400,
            dynamic_resizing=False
        )
        self.submodule_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
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
            self.branch_var.set("")
            self.submodule_var.set("")
            self.selected_branch = ""
            self.selected_submodule = ""
            
            # Initialize with new repository
            self._initialize_version_finder()
            
            self._log_output(f"Selected repository: {self.repo_path}")
        else:
            self._log_output("No directory selected")

    def _update_branch_dropdown(self):
        """Update the branch dropdown with the current branch"""
        if self.version_finder:
            branches = self.version_finder.list_branches()
            self.branch_dropdown.configure(values=branches)
            self.selected_branch = self.version_finder.get_current_branch()
            if self.selected_branch and self.selected_branch in branches:
                self.branch_var.set(self.selected_branch)
                self._log_output("Loaded branches successfully.")
                self._on_branch_select(self.selected_branch)

    def _initialize_version_finder(self):
        """Initialize the VersionFinder with the selected repository path"""
        try:
            # Initialize the repository
            self.init_repo(self.repo_path)
        except Exception as e:
            logger.error(f"Error initializing VersionFinder: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize repository: {str(e)}")
            
    def _handle_branches_loaded(self, branches, error=None):
        """Handle branches loaded from worker process"""
        if error:
            self._log_error(f"Error loading branches: {error}")
            return
            
        if not branches:
            self._log_warning("No branches found in repository")
            return
            
        # Update branch dropdown
        self.branch_var.set("")
        self.branch_dropdown.configure(values=branches)
        
        # Select first branch by default
        self.branch_var.set(branches[0])
        self.selected_branch = branches[0]
        
        self._log_output(f"Loaded {len(branches)} branches")
        
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
        
    def _handle_submodules_loaded(self, submodules, error=None):
        """Handle submodules loaded from worker process"""
        if error:
            return
            
        # Update submodule dropdown
        self.submodule_var.set("")
        self.submodule_dropdown.configure(values=[""] + submodules)
        
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

        if not self.branch_var.get():
            messagebox.showerror("Error", "Please select a branch")
            return False

        # Check if repository is initialized
        if self.version_finder is None:
            self._log_warning("Repository not initialized, attempting to initialize now")
            self._initialize_version_finder()
            # Return False to prevent proceeding until initialization is complete
            return False

        return True

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