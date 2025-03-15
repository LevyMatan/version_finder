import multiprocessing
import time
import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox
import atexit

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('destructor_test.log')
    ]
)

logger = logging.getLogger('DestructorTest')

class TestObject:
    """A test class with a destructor to demonstrate when it gets called."""
    
    def __init__(self, name):
        self.name = name
        self._state_saved = True  # Simulate having saved state
        logger.info(f"{self.name} created")
        
    def __del__(self):
        """Destructor that logs when it's called."""
        try:
            logger.info(f"Destructor called for {self.name}")
            # Simulate restoring state
            if hasattr(self, '_state_saved') and self._state_saved:
                logger.info(f"Restoring state for {self.name}")
                time.sleep(0.5)  # Simulate work
                logger.info(f"State restored for {self.name}")
        except Exception as e:
            logger.error(f"Error in destructor: {e}")

def worker_process(name, queue, exit_event=None):
    """Worker process that creates a TestObject."""
    logger.info(f"Worker process {name} started (PID: {os.getpid()})")
    
    # Register exit handler
    def exit_handler():
        logger.info(f"Exit handler called for worker {name}")
    
    atexit.register(exit_handler)
    
    # Create test object
    test_obj = TestObject(f"Object in {name}")
    
    # Wait for commands
    while True:
        try:
            if exit_event and exit_event.is_set():
                logger.info(f"Worker {name} detected exit event")
                break
                
            command = queue.get(timeout=1)
            if command == "exit":
                logger.info(f"Worker {name} received exit command")
                # Explicitly delete the object before exiting
                logger.info(f"Worker {name} explicitly deleting object")
                del test_obj
                break
        except:
            pass
            
    logger.info(f"Worker process {name} exiting")

class SimpleGUI(tk.Tk):
    """A simple GUI to test destructor behavior with tkinter."""
    
    def __init__(self):
        super().__init__()
        self.title("Destructor Test")
        self.geometry("500x400")
        
        # Create a test object
        self.test_obj = TestObject("GUI Object")
        
        # Setup multiprocessing
        self.queue = multiprocessing.Queue()
        self.exit_event = multiprocessing.Event()
        
        # Create daemon worker
        self.daemon_worker = multiprocessing.Process(
            target=worker_process,
            args=("DaemonWorker", self.queue),
            daemon=True
        )
        
        # Create non-daemon worker
        self.non_daemon_worker = multiprocessing.Process(
            target=worker_process,
            args=("NonDaemonWorker", self.queue, self.exit_event),
            daemon=False
        )
        
        # Start workers
        self.daemon_worker.start()
        self.non_daemon_worker.start()
        
        logger.info(f"Daemon worker PID: {self.daemon_worker.pid}")
        logger.info(f"Non-daemon worker PID: {self.non_daemon_worker.pid}")
        
        # Create buttons
        tk.Button(self, text="Test 1: Normal Exit", 
                  command=self.normal_exit).pack(pady=10)
        
        tk.Button(self, text="Test 2: Force GC", 
                  command=self.force_gc).pack(pady=10)
        
        tk.Button(self, text="Test 3: Exit Daemon Worker", 
                  command=self.exit_daemon_worker).pack(pady=10)
        
        tk.Button(self, text="Test 4: Exit Non-Daemon Worker", 
                  command=self.exit_non_daemon_worker).pack(pady=10)
        
        tk.Button(self, text="Test 5: Exit Both Workers", 
                  command=self.exit_both_workers).pack(pady=10)
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Register exit handler
        atexit.register(self.atexit_handler)
        
    def atexit_handler(self):
        """Handler called when the program exits."""
        logger.info("Atexit handler called for GUI")
        
    def normal_exit(self):
        """Test normal exit."""
        logger.info("Normal exit test")
        self.destroy()
        
    def force_gc(self):
        """Test forcing garbage collection."""
        import gc
        logger.info("Forcing garbage collection")
        gc.collect()
        messagebox.showinfo("GC", "Garbage collection forced")
        
    def exit_daemon_worker(self):
        """Test exiting the daemon worker."""
        logger.info("Sending exit command to daemon worker")
        self.queue.put("exit")
        messagebox.showinfo("Worker", "Exit command sent to daemon worker")
        
    def exit_non_daemon_worker(self):
        """Test exiting the non-daemon worker."""
        logger.info("Setting exit event for non-daemon worker")
        self.exit_event.set()
        messagebox.showinfo("Worker", "Exit event set for non-daemon worker")
        
    def exit_both_workers(self):
        """Test exiting both workers."""
        logger.info("Exiting both workers")
        self.queue.put("exit")  # For daemon worker
        self.exit_event.set()   # For non-daemon worker
        messagebox.showinfo("Workers", "Exit commands sent to both workers")
        
    def on_close(self):
        """Handle window close event."""
        logger.info("Window close event")
        
        # Method 1: Just destroy
        # self.destroy()
        
        # Method 2: Try to clean up explicitly
        logger.info("Cleaning up before exit")
        
        # Send exit to workers
        self.queue.put("exit")  # For daemon worker
        self.exit_event.set()   # For non-daemon worker
        
        # Wait a moment for workers to process
        self.after(1000, self._complete_shutdown)
        
    def _complete_shutdown(self):
        """Complete the shutdown process."""
        logger.info("Completing shutdown")
        
        # Wait for non-daemon worker to finish (with timeout)
        if self.non_daemon_worker.is_alive():
            logger.info("Waiting for non-daemon worker to finish")
            self.non_daemon_worker.join(timeout=2)
            if self.non_daemon_worker.is_alive():
                logger.warning("Non-daemon worker did not exit, terminating")
                self.non_daemon_worker.terminate()
        
        # Explicitly delete the object
        if hasattr(self, 'test_obj'):
            logger.info("Explicitly deleting GUI object during shutdown")
            del self.test_obj
            
        # Now destroy the window
        self.destroy()

def main():
    """Main function to run the test."""
    logger.info("Starting destructor test")
    
    # Register exit handler
    def exit_handler():
        logger.info("Main process exit handler called")
    
    atexit.register(exit_handler)
    
    # Test 1: Simple object creation and deletion
    logger.info("=== Test 1: Simple object ===")
    obj = TestObject("Simple Object")
    del obj
    
    # Test 2: Object in a function
    logger.info("=== Test 2: Function scope ===")
    def test_function():
        obj = TestObject("Function Object")
        # Object should be deleted when function exits
    test_function()
    
    # Test 3: GUI test
    logger.info("=== Test 3: GUI test ===")
    app = SimpleGUI()
    app.mainloop()
    
    logger.info("GUI mainloop exited")
    
    # Force garbage collection at the end
    import gc
    logger.info("Forcing final garbage collection")
    gc.collect()
    
    logger.info("Test completed")

if __name__ == "__main__":
    main() 