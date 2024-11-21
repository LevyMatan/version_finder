from tkinter import filedialog, ttk
import tkinter as tk
from PIL import Image, ImageTk
import argparse
import os
from .__common__ import parse_arguments
os.environ['TK_SILENCE_DEPRECATION'] = '1'

__gui_version__ = '0.1.0'


class VersionFinderGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.center_window()
        self.setup_styles()
        self.create_widgets()
        self.setup_icon()

    def setup_window(self):
        self.root.title("Version Finder")
        self.window_height = 800
        self.window_width = 600
        self.root.geometry(f"{self.window_height}x{self.window_width}")
        self.root.minsize(600, 400)

        # Configure main window grid and background
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.configure(bg='#f0f0f0')

    def center_window(self, width=None, height=None):
        window = self.root
        if width is None:
            width = self.window_width
        if height is None:
            height = self.window_height
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position to center the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Set window size and position
        window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()

        # Configure frame styles
        style.configure('Main.TFrame', background='#f0f0f0')

        # Configure label styles
        style.configure('Header.TLabel',
                        font=('Helvetica', 24, 'bold'),
                        foreground='#2c3e50',
                        background='#f0f0f0',
                        padding=10)

        style.configure('Directory.TLabel',
                        font=('Helvetica', 12),
                        foreground='#34495e',
                        background='#f0f0f0',
                        padding=5)

        # Configure button styles
        style.configure('Action.TButton',
                        font=('Helvetica', 11),
                        padding=10)

        style.configure('Browse.TButton',
                        font=('Helvetica', 11),
                        padding=5)

    def create_widgets(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        # Header
        header = ttk.Label(self.main_frame,
                           text="Version Finder",
                           style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))

        # Directory selection
        self.create_directory_section()

        # Output area
        self.create_output_area()

        # Buttons and status bar
        self.create_buttons()
        self.create_status_bar()

    def setup_icon(self):
        # Set the icon for the application
        icon_path = os.path.join(os.path.dirname(__file__), 'assets/icon.png')
        if os.path.exists(icon_path):
            # Load the image
            icon = Image.open(icon_path)
            icon = ImageTk.PhotoImage(icon)

            # Set the icon
            self.root.wm_iconphoto(True, icon)

    def create_directory_section(self):
        dir_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        dir_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame,
                  text="Select Directory:",
                  style='Directory.TLabel').grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Directory entry with modern styling
        self.dir_entry = ttk.Entry(dir_frame, font=('Helvetica', 11))
        self.dir_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Button(dir_frame,
                   text="Browse",
                   style='Browse.TButton',
                   command=self.browse_directory).grid(row=0, column=2, padx=(5, 0))

    def create_output_area(self):
        # Create frame for output
        output_frame = ttk.LabelFrame(self.main_frame,
                                      text="Search Results",
                                      style='Main.TFrame',
                                      padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        # Create text widget and scrollbar
        self.output_text = tk.Text(
            output_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            background="white",
            relief="flat",
            padx=10,
            pady=10
        )
        scrollbar = ttk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.output_text.yview
        )

        self.output_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text['yscrollcommand'] = scrollbar.set

    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # Search button
        ttk.Button(
            button_frame,
            text="Search",
            style='Action.TButton',
            command=self.search
        ).grid(row=0, column=0, padx=5)

        # Clear button
        ttk.Button(
            button_frame,
            text="Clear",
            style='Action.TButton',
            command=self.clear_output
        ).grid(row=0, column=1, padx=5)

        # Exit button
        ttk.Button(
            button_frame,
            text="Exit",
            style='Action.TButton',
            command=self.root.quit
        ).grid(row=0, column=2, padx=5)

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.main_frame,
                               textvariable=self.status_var,
                               relief=tk.SUNKEN,
                               padding=(10, 5))
        status_bar.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 0))

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.status_var.set(f"Selected directory: {directory}")

    def search(self):
        directory = self.dir_entry.get()
        if not directory:
            self.output_text.insert(tk.END, "⚠️ Please select a directory first.\n")
            self.status_var.set("Error: No directory selected")
            return

        self.status_var.set("Searching...")
        self.output_text.insert(tk.END, f"🔍 Searching in: {directory}\n")
        # Add your version finding logic here
        self.output_text.see(tk.END)

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("Output cleared")

    def run_mainloop(self):
        self.root.mainloop()

    def bring_to_front(self):
        self.root.focus_force()


def gui_main(args: argparse.Namespace) -> int:
    root = tk.Tk()
    app = VersionFinderGUI(root)
    app.bring_to_front()
    app.run_mainloop()


def main():
    args = parse_arguments()
    gui_main(args)


if __name__ == "__main__":
    main()
