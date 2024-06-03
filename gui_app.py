import tkinter as tk
from tkinter import messagebox
from version_finder import VersionFinder

def find_version():
    path = path_entry.get()
    branch = branch_entry.get()
    commit = commit_entry.get()
    submodule = submodule_entry.get()

    version_finder = VersionFinder(path)
    if not version_finder.isValidBranch(branch):
        messagebox.showerror("Error", "Invalid branch")
        return

    if submodule and not version_finder.isValidSubmodule(submodule):
        messagebox.showerror("Error", "Invalid submodule")
        return

    if not version_finder.isValidCommitSha(commit, branch, submodule):
        messagebox.showerror("Error", "Invalid commit SHA")
        return

    version = version_finder.find_first_commit_with_version(commit, branch, submodule)
    if version:
        messagebox.showinfo("Version", version)
    else:
        messagebox.showinfo("Version", "No version found in the logs.")

root = tk.Tk()

path_label = tk.Label(root, text="Repository Path")
path_label.pack()
path_entry = tk.Entry(root)
path_entry.pack()

branch_label = tk.Label(root, text="Branch Name")
branch_label.pack()
branch_entry = tk.Entry(root)
branch_entry.pack()

commit_label = tk.Label(root, text="Commit SHA")
commit_label.pack()
commit_entry = tk.Entry(root)
commit_entry.pack()

submodule_label = tk.Label(root, text="Submodule Path (optional)")
submodule_label.pack()
submodule_entry = tk.Entry(root)
submodule_entry.pack()

find_button = tk.Button(root, text="Find Version", command=find_version)
find_button.pack()

root.mainloop()