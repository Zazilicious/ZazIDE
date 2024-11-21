#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
import subprocess
import re

# Root window setup
root = Tk()
root.title("ZazIDE")
root.geometry("800x600")

global opened_name
opened_name = False

global selected
selected = False

# Update syntax highlighting for Python code
def highlight_syntax(e=False):
    m_text.tag_remove("keyword", "1.0", END)
    m_text.tag_remove("comment", "1.0", END)
    m_text.tag_remove("string", "1.0", END)

    python_keywords = ["def", "class", "import", "from", "if", "else", "elif", "for", "while", "return", "break", "continue", "try", "except", "finally", "in", "then"]
    for keyword in python_keywords:
        idx = '1.0'
        while True:
            idx = m_text.search(r'\y' + keyword + r'\y', idx, nocase=True, stopindex=END, regexp=True)
            if not idx:
                break
            end_idx = f"{idx}+{len(keyword)}c"
            m_text.tag_add("keyword", idx, end_idx)
            m_text.tag_configure("keyword", foreground="blue")
            idx = end_idx

    comment_pattern = r'#.*'
    idx = '1.0'
    while True:
        idx = m_text.search(comment_pattern, idx, nocase=True, stopindex=END, regexp=True)
        if not idx:
            break
        end_idx = f"{idx} lineend"
        m_text.tag_add("comment", idx, end_idx)
        m_text.tag_configure("comment", foreground="green")
        idx = end_idx

    string_pattern = r'\".*?\"|\'[^\']*\''
    idx = '1.0'
    while True:
        idx = m_text.search(string_pattern, idx, nocase=True, stopindex=END, regexp=True)
        if not idx:
            break
        end_idx = f"{idx}+{len(m_text.get(idx, f'{idx} lineend'))}c"
        m_text.tag_add("string", idx, end_idx)
        m_text.tag_configure("string", foreground="red")
        idx = end_idx

# Create new file
def new_file():
    m_text.delete("1.0", END)
    root.title("New File")
    global opened_name
    opened_name = False

# Open file
def open_file():
    m_text.delete("1.0", END)
    t_file = filedialog.askopenfilename(initialdir="~/", title="Open File",
                                        filetypes=(("Python", "*.py"), ("HTML Files", "*.html"),
                                                  ("Text Files", "*.txt"), ("All Files", "*.*")))
    if t_file:
        global opened_name
        opened_name = t_file
        name = t_file
        t_file = open(t_file, 'r')
        stuff = t_file.read()
        m_text.insert(END, stuff)
        t_file.close()
        root.title(f"Editing: {name}")
        highlight_syntax()

# Save file
def save_as_file(e=False):
    global opened_name
    t_file = filedialog.asksaveasfilename(defaultextension=".py", initialdir="~/", title="Save File",
                                         filetypes=(("Python Files", "*.py"), ("HTML Files", "*.html"),
                                                   ("Text Files", "*.txt"), ("All Files", "*.*")))
    opened_name = t_file
    t_file = open(t_file, 'w')
    t_file.write(m_text.get(1.0, END))
    t_file.close()
    root.title(f"Editing: {opened_name}")

# Save file
def save_file(e=False):
    global opened_name
    if opened_name:
        t_file = open(opened_name, 'w')
        t_file.write(m_text.get(1.0, END))
        t_file.close()
        messagebox.showinfo("Saved", "File saved successfully")
    else:
        save_as_file()

# Cut text
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

# Copy text
def copy_text(e=False):
    global selected
    if e:
        selected = root.clipboard_get()
    if m_text.selection_get():
        selected = m_text.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)

# Paste text
def paste_text(e=False):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if selected:
            position = m_text.index(INSERT)
            m_text.insert(position, selected)

# Select all
def select_all(e=False):
    m_text.tag_add('sel', '1.0', 'end')

# Clear all
def clear_all(e=False):
    m_text.delete(1.0, END)

# Run Python code
def run_code():
    try:
        exec(m_text.get(1.0, END))
    except Exception as e:
        messagebox.showerror("Error", f"Error executing code:\n{str(e)}")

# Find text
def find_text():
    find_popup = Toplevel(root)
    find_popup.title("Find")
    find_popup.geometry("300x100")
    Label(find_popup, text="Find:").pack(pady=5)
    find_entry = Entry(find_popup, width=30)
    find_entry.pack(pady=5)
    Button(find_popup, text="Find", command=lambda: search_text(find_entry.get(), find_popup)).pack(pady=5)

def search_text(query, popup):
    idx = '1.0'
    while True:
        idx = m_text.search(query, idx, nocase=True, stopindex=END)
        if not idx:
            break
        end_idx = f"{idx}+{len(query)}c"
        m_text.tag_add("search", idx, end_idx)
        m_text.tag_configure("search", background="yellow")
        idx = end_idx
    popup.destroy()

# Frame and Text Widget
m_frame = Frame(root)
m_frame.pack(pady=5, padx=5)

# Scrollbar
t_scroll = Scrollbar(m_frame)
t_scroll.pack(side=RIGHT, fill=Y)

# Textbox
m_text = Text(m_frame, width=150, height=30, font=("Calibri", 16), selectbackground="yellow",
              selectforeground="black", undo=True)
m_text.pack(side=RIGHT)
m_text.bind("<KeyRelease>", highlight_syntax)

# Config scrollbar
t_scroll.config(command=m_text.yview)
m_text.config(yscrollcommand=t_scroll.set)

# Menu bar
m_menu = Menu(root)
root.config(menu=m_menu)

# File menu
f_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="File", menu=f_menu)
f_menu.add_command(label="New", command=new_file)
f_menu.add_command(label="Open", command=open_file)
f_menu.add_command(label="Save", command=save_file)
f_menu.add_command(label="Save as", command=save_as_file)
f_menu.add_separator()
f_menu.add_command(label="Exit", command=root.quit)

# Edit menu
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
e_menu.add_separator()

# Run menu
r_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Run", menu=r_menu)
r_menu.add_command(label="Run Python", command=run_code)

# Search menu
s_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Search", menu=s_menu)
s_menu.add_command(label="Find", command=find_text)

# Edit bindings
root.bind('<Control-Key-x>', cut_text)
root.bind('<Control-Key-c>', copy_text)
root.bind('<Control-Key-v>', paste_text)
root.bind('<Control-Key-A>', select_all)
root.bind('<Control-Key-a>', select_all)
root.bind('<Control-Key-s>', save_file)
root.bind('<Control-Key-S>', save_as_file)

# Initial setup
root.mainloop()

