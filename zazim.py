#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import simpledialog
import subprocess
import re
import json
import os
import sys

# Pyinstaller stuff
def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    When bundled, PyInstaller stores data files in a temp folder accessible via sys._MEIPASS.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# Root window setup
root = Tk()
root.title("ZazIDE")
root.geometry("800x600")

global opened_name
opened_name = False

global selected
selected = False

# Load syntax highlighting rules (uses resource_path for PyInstaller)
try:
    with open(resource_path("syntax_rules.json"), "r", encoding="utf-8") as f:
        syntax_rules = json.load(f)
except Exception as e:
    syntax_rules = {}
    messagebox.showerror(
        "syntax_rules.json not found",
        f"Could not load syntax_rules.json:\n{e}\n\n"
        "If you are running a bundled executable, ensure you passed --add-data:\n"
        "  Windows: pyinstaller --add-data \"syntax_rules.json;.\" ...\n"
        "  macOS/Linux: pyinstaller --add-data \"syntax_rules.json:.\" ..."
    )

# Update syntax highlighting

def highlight_syntax(e=False):
    m_text.tag_remove("keyword", "1.0", END)
    m_text.tag_remove("comment", "1.0", END)
    m_text.tag_remove("string", "1.0", END)

    global syntax_rules

    file_extension = (opened_name.split('.')[-1] if opened_name else "").lower()
    if file_extension == "py":
        lang = "python"
    elif file_extension == "lua":
        lang = "lua"
    elif file_extension in ["js", "mjs", "cjs"]:
        lang = "javascript"
    elif file_extension == "p8":
        lang = "puls8"
    elif file_extension == "c":
        lang = "c"
    elif file_extension in ["cpp", "cc", "c++", "cp"]:
        lang = "cpp"
    elif file_extension == "html":
        lang = "html"
    elif file_extension == "css":
        lang = "css"
    else:
        lang = None

    if lang and lang in syntax_rules:
        rules = syntax_rules[lang]

        keyword_pattern = r'(?<!\w)(' + '|'.join(re.escape(keyword) for keyword in rules["keywords"]) + r')(?!\w)'
        for match in re.finditer(keyword_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("keyword", start_idx, end_idx)
            m_text.tag_configure("keyword", foreground="blue")

        comment_pattern = rules["comment"]
        for match in re.finditer(comment_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("comment", start_idx, end_idx)
            m_text.tag_configure("comment", foreground="green")

        string_pattern = rules["string"]
        for match in re.finditer(string_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("string", start_idx, end_idx)
            m_text.tag_configure("string", foreground="red")
# i[date cursor 
def update_cursor_position(event=None):
    cursor_position = m_text.index(INSERT)
    current_line = cursor_position.split('.')[0]
    line_count_label.config(text=f"Line: {current_line}")
# new file
def new_file():
    m_text.delete("1.0", END)
    root.title("New File")
    global opened_name
    opened_name = False
    update_cursor_position()
# open file
def open_file():
    m_text.delete("1.0", END)
    t_file = filedialog.askopenfilename(initialdir="~/", title="Open File",
                                        filetypes=(("Python", "*.py"), ("Lua Files", "*.lua"), ("Puls8 Files", "*.p8"), 
                                                   ("JavaScript Files", "*.js"),("C Files", "*.c"),("HTML Files", "*.html"),("CSS Files", "*.css"),("C++ Files", "*.cpp"),("All Files", "*.*")))
    if t_file:
        global opened_name
        opened_name = t_file
        name = t_file
        with open(t_file, 'r') as f:
            stuff = f.read()
        m_text.insert(END, stuff)
        root.title(f"Editing: {name}")
        highlight_syntax()
        update_cursor_position()
#save file as
def save_as_file(e=False):
    global opened_name
    t_file = filedialog.asksaveasfilename(defaultextension=".py", initialdir="~/", title="Save File",
                                         filetypes=(("Python Files", "*.py"), ("Lua Files", "*.lua"), ("Puls8 Files", "*.p8"), 
                                                    ("JavaScript Files", "*.js"),("C Files", "*.c"),("C++ Files", "*.cpp"), ("HTML Files", "*.html"),("CSS Files", "*.css"),("All Files", "*.*")))
    opened_name = t_file
    with open(t_file, 'w') as f:
        f.write(m_text.get(1.0, END))
    root.title(f"Editing: {opened_name}")
# save file
def save_file(e=False):
    global opened_name
    if opened_name:
        with open(opened_name, 'w') as f:
            f.write(m_text.get(1.0, END))
        messagebox.showinfo("Saved", "File saved successfully")
    else:
        save_as_file()
# cut text
def cut_text(e=False):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if m_text.selection_get():
            selected = m_text.selection_get()
            m_text.delete("sel.first", "sel.last")
            root.clipboard_clear()
            root.clipboard_append(selected)
# copy text
def copy_text(e=False):
    global selected
    if e:
        selected = root.clipboard_get()
    if m_text.selection_get():
        selected = m_text.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)
# paste text
def paste_text(e=False):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if selected:
            position = m_text.index(INSERT)
            m_text.insert(position, selected)

# find text
def find_text(e=False):
    def do_find():
        query = entry.get()
        m_text.tag_remove("highlight", "1.0", "end")
        if not query:
            return

        m_text.tag_config("highlight", background="yellow", foreground="black")
        start_pos = "1.0"
        first_match_idx = None
        while True:
            idx = m_text.search(query, start_pos, stopindex="end", nocase=1)
            if not idx:
                break
            end_idx = f"{idx}+{len(query)}c"
            m_text.tag_add("highlight", idx, end_idx)

            if first_match_idx is None:
                first_match_idx = idx

            start_pos = end_idx

        if first_match_idx:
            m_text.mark_set("insert", first_match_idx)
            m_text.see(first_match_idx)
        else:
            messagebox.showinfo("Find", f"No matches for: {query}")

    def on_close():
        m_text.tag_remove("highlight", "1.0", "end")
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title("Find")
    popup.geometry("300x80")
    popup.transient(root)
    popup.grab_set()

    tk.Label(popup, text="Enter text to find:").pack(pady=5)
    entry = tk.Entry(popup, width=30)
    entry.pack(pady=2)
    entry.focus()

    tk.Button(popup, text="Find", command=do_find).pack(pady=5)

    popup.protocol("WM_DELETE_WINDOW", on_close)

# select all
def select_all(e=False):
    m_text.tag_add('sel', '1.0', 'end')
# clear all
def clear_all(e=False):
    m_text.delete(1.0, END)
# run code
def run_code():
    try:
        exec(m_text.get(1.0, END))
    except Exception as e:
        messagebox.showerror("Error", f"Error executing code:\n{str(e)}")

# settings
def apply_resolution(res):
    if res == "Fullscreen":
        root.attributes("-fullscreen", True)
    else:
        root.attributes("-fullscreen", False)
        root.geometry(res)

# dark mode stuff
dark_mode_enabled = True  

def toggle_dark_mode():
    global dark_mode_enabled
    dark_mode_enabled = not dark_mode_enabled

    bg_color = "#2E3440" if dark_mode_enabled else "white"
    fg_color = "#D8DEE9" if dark_mode_enabled else "black"
    insert_bg = "#D8DEE9" if dark_mode_enabled else "black"

    m_text.config(bg=bg_color, fg=fg_color, insertbackground=insert_bg)
    line_count_label.config(bg=bg_color, fg=fg_color)

    m_menu.config(bg=bg_color, fg=fg_color)
    for menu in [f_menu, e_menu, r_menu, s_menu]:
        menu.config(bg=bg_color, fg=fg_color)

def apply_dark_mode():
    bg_color = "#2E3440"
    fg_color = "#D8DEE9"
    insert_bg = "#D8DEE9"

    m_text.config(bg=bg_color, fg=fg_color, insertbackground=insert_bg)
    line_count_label.config(bg=bg_color, fg=fg_color)

    m_menu.config(bg=bg_color, fg=fg_color)
    for menu in [f_menu, e_menu, r_menu, s_menu]:
        menu.config(bg=bg_color, fg=fg_color)

# Automatic indentation
def auto_indent(event):
    cursor_index = m_text.index(INSERT)
    line_number = cursor_index.split('.')[0]
    current_line_text = m_text.get(f"{line_number}.0", f"{line_number}.end")
    indentation = re.match(r"[ \t]*", current_line_text).group()
    if current_line_text.rstrip().endswith(":"):
        indentation += "    "
    m_text.insert(cursor_index, "\n" + indentation)
    m_text.mark_set(INSERT, f"{line_number}.end + {len(indentation)+1}c")
    return "break"


# Frame and Text Widget
m_frame = Frame(root)
m_frame.pack(pady=5, padx=5)

t_scroll = Scrollbar(m_frame)
t_scroll.pack(side=RIGHT, fill=Y)

m_text = Text(m_frame, width=200, height=50, font=("Calibri", 16), selectbackground="yellow",
              selectforeground="black", undo=True)
m_text.pack(side=RIGHT)
m_text.bind("<KeyRelease>", lambda e: [highlight_syntax(e), update_cursor_position(e)])
m_text.bind("<Return>", auto_indent)

t_scroll.config(command=m_text.yview)
m_text.config(yscrollcommand=t_scroll.set)

# Menu bar
m_menu = Menu(root)
root.config(menu=m_menu)

f_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="File", menu=f_menu)
f_menu.add_command(label="New", command=new_file)
f_menu.add_command(label="Open", command=open_file)
f_menu.add_command(label="Save", command=save_file)
f_menu.add_command(label="Save as", command=save_as_file)
f_menu.add_separator()
f_menu.add_command(label="Exit", command=root.quit)

e_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Edit", menu=e_menu)
e_menu.add_command(label="Cut   (Ctrl+X)", command=cut_text)
e_menu.add_command(label="Copy   (Ctrl+C)", command=copy_text)
e_menu.add_command(label="Paste   (Ctrl+V)", command=paste_text)
e_menu.add_separator()
e_menu.add_command(label="Undo", command=m_text.edit_undo)
e_menu.add_command(label="Redo", command=m_text.edit_redo)
e_menu.add_separator()
e_menu.add_command(label="Select All", command=select_all)
e_menu.add_command(label="Clear", command=clear_all)
e_menu.add_command(label="Find", command=find_text)

r_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Run", menu=r_menu)
r_menu.add_command(label="Run Python", command=run_code)

s_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Settings", menu=s_menu)

res_menu = Menu(s_menu, tearoff=False)
s_menu.add_cascade(label="Resolution", menu=res_menu)
res_menu.add_command(label="800x600", command=lambda: apply_resolution("800x600"))
res_menu.add_command(label="1024x768", command=lambda: apply_resolution("1024x768"))
res_menu.add_command(label="1280x720", command=lambda: apply_resolution("1280x720"))
res_menu.add_command(label="Fullscreen", command=lambda: apply_resolution("Fullscreen"))

s_menu.add_separator()
s_menu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)

# Status bar
line_count_label = Label(root, text="Line: 1", bd=1, relief=SUNKEN, anchor=W)
line_count_label.pack(fill=X, side=BOTTOM)

# Keyboard shortcuts
root.bind("<Control-Key-x>", cut_text)
root.bind("<Control-Key-c>", copy_text)
root.bind("<Control-Key-v>", paste_text)
root.bind('<Control-Key-A>', select_all)
root.bind('<Control-Key-a>', select_all)
root.bind("<Control-Key-s>", save_file)
root.bind("<Command-Key-s>", save_file)
root.bind("<Control-Key-f>", lambda e: find_text())
# more dark mode stuff
if dark_mode_enabled:
    apply_dark_mode()

# Start main loop
root.mainloop()
