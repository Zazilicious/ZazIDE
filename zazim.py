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

# Update syntax highlighting for Python, Lua, and JavaScript code
def highlight_syntax(e=False):
    m_text.tag_remove("keyword", "1.0", END)
    m_text.tag_remove("comment", "1.0", END)
    m_text.tag_remove("string", "1.0", END)

    # Define syntax rules
    syntax_rules = {
        "python": {
            "keywords": ["def", "class", "import", "from", "if", "else", "elif", "for", "while", "return", "break", "continue", "try", "except", "finally", "in", "then"],
            "comment": r'#.*',
            "string": r'".*?"|\'.*?\''
        },
        "lua": {
            "keywords": ["function", "end", "if", "then", "else", "elseif", "for", "while", "do", "local", "return", "break"],
            "comment": r'--.*',
            "string": r'".*?"|\'.*?\''
        },
        "javascript": {
            "keywords": ["function", "var", "let", "const", "if", "else", "for", "while", "return", "break", "continue", "class", "import", "export", "try", "catch", "finally"],
            "comment": r'//.*',
            "string": r'".*?"|\'.*?\''
        },
        "puls8": {
            "keywords": ["NOP","nop", "STC","stc", "STD","std", "ADD","add", "LDCI","ldci", "LDD","ldd", "LDC","ldc", "PUSHI","pushi", "PUSHA","pusha", "LDB","ldb", "LDA","lda", "POUT","pout", "STA","sta", "STB","stb", "RSH","rsh", "HLT","hlt", "JMP","jmp", "SUB","sub", "JC","jc", "JZ","jz", "LDAI","ldai", "PIN","pin", "PSTAT","pstat", "CMP","cmp", "CMPI","cmpi", "AND","and", "ANDI","andi", "JNZ","jnz", "LDDI","lddi", "LDACD","ldacd", "LDBI","ldbi", "PUSHB","pushb", "JSR","jsr", "VLFB","vlfb", "VFBW","vfbw", "STACD","stacd", "ADDI","addi", "VFBBG","vfbbg", "AVAIL18","avail18", "AVAIL19","avail19", "AVAIL1A","avail1a", "AVAIL1B","avail1b", "AVAIL1C","avail1c", "AVAIL1D","avail1d", "AVAIL1E", "avail1e", "AVAIL1F","avail1f", "AVAIL20","avail20", "AVAIL21","avail21", "AVAIL22","avail22", "AVAIL23","avail23", "AVAIL24","avail24", "AVAIL25","avail25", "AVAIL26","avail26", "AVAIL27","avail27", "AIL28","avail28", "AVAIL29","avail29", "AVAIL2A","avail2a", "AVAIL2B","avail2b", "AVAIL2C","avail2c", "AVAIL2D","avail2d", "AVAIL2E","avail2e", "AVAIL2F","avail2f", "AVAIL30","avail30", "AVAIL31","avail31", "RTS","rts","PUSHC","PUSHD","SUBI","POPC","POPD"],
            "comment": r'\;.*',
            "string": r'".*?"'
        },
        
        "c": {
        "keywords": ["auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"],
        "comment": r'//.*|/\*[\s\S]*?\*/',
        "string": r'".*?"|\'.*?\''
        },
        "cpp": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor", "bool", "break", "case", "catch", "char", "char16_t", "char32_t", "class", "const", "const_cast", "continue", "decltype", "default", "delete", "do", "double", "dynamic_cast", "else", "enum", "explicit", "export", "extern", "false", "final", "float", "for", "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace", "new", "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private", "protected", "public", "register", "reinterpret_cast", "return", "short", "signed", "sizeof", "static", "static_assert", "static_cast", "struct", "switch", "template", "this", "thread_local", "throw", "true", "try", "typedef", "typeid", "typename", "union", "unsigned", "using", "virtual", "void", "volatile", "wchar_t", "while"],
        "comment": r'//.*|/\*[\s\S]*?\*/',
        "string": r'".*?"|\'.*?\''
        }
    }

    # Detect language based on the file extension
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
    elif file_extension == "cpp":
        lang = "cpp"
    elif file_extension == "cc":
        lang = "cpp"
    elif file_extension == "c++":
        lang = "cpp"
    elif file_extension == "cp":
        lang = "cpp"
    else:
        lang = None

    if lang and lang in syntax_rules:
        rules = syntax_rules[lang]

        # Highlight keywords
        keyword_pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in rules["keywords"]) + r')\b'
        for match in re.finditer(keyword_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("keyword", start_idx, end_idx)
            m_text.tag_configure("keyword", foreground="blue")

        # Highlight comments
        comment_pattern = rules["comment"]
        for match in re.finditer(comment_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("comment", start_idx, end_idx)
            m_text.tag_configure("comment", foreground="green")

        # Highlight strings
        string_pattern = rules["string"]
        for match in re.finditer(string_pattern, m_text.get("1.0", "end-1c")):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            m_text.tag_add("string", start_idx, end_idx)
            m_text.tag_configure("string", foreground="red")

# Update the line counter at the bottom of the screen to show the current line
def update_cursor_position(event=None):
    cursor_position = m_text.index(INSERT)
    current_line = cursor_position.split('.')[0]
    line_count_label.config(text=f"Line: {current_line}")

# Create new file
def new_file():
    m_text.delete("1.0", END)
    root.title("New File")
    global opened_name
    opened_name = False
    update_cursor_position()

# Open file and determine syntax
def open_file():
    m_text.delete("1.0", END)
    t_file = filedialog.askopenfilename(initialdir="~/", title="Open File",
                                        filetypes=(("Python", "*.py"), ("Lua Files", "*.lua"), ("Puls8 Files", "*.p8"), 
                                                   ("JavaScript Files", "*.js"),("C Files", "*.c"),("C++ Files", "*.cpp"),("All Files", "*.*")))
    if t_file:
        global opened_name
        opened_name = t_file
        name = t_file
        with open(t_file, 'r') as f:
            stuff = f.read()
        m_text.insert(END, stuff)
        root.title(f"Editing: {name}")
        highlight_syntax()  # Trigger syntax highlighting after loading
        update_cursor_position()

# Save file
def save_as_file(e=False):
    global opened_name
    t_file = filedialog.asksaveasfilename(defaultextension=".py", initialdir="~/", title="Save File",
                                         filetypes=(("Python Files", "*.py"), ("Lua Files", "*.lua"), ("Puls8 Files", "*.p8"), 
                                                    ("JavaScript Files", "*.js"),("C Files", "*.c"),("C++ Files", "*.cpp"), ("All Files", "*.*")))
    opened_name = t_file
    with open(t_file, 'w') as f:
        f.write(m_text.get(1.0, END))
    root.title(f"Editing: {opened_name}")

def save_file(e=False):
    global opened_name
    if opened_name:
        with open(opened_name, 'w') as f:
            f.write(m_text.get(1.0, END))
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

# Frame and Text Widget
m_frame = Frame(root)
m_frame.pack(pady=5, padx=5)

# Scrollbar
t_scroll = Scrollbar(m_frame)
t_scroll.pack(side=RIGHT, fill=Y)

# Textbox
m_text = Text(m_frame, width=200, height=50, font=("Calibri", 16), selectbackground="yellow",
              selectforeground="black", undo=True)
m_text.pack(side=RIGHT)
m_text.bind("<KeyRelease>", lambda e: [highlight_syntax(e), update_cursor_position(e)])

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

# Run menu
r_menu = Menu(m_menu, tearoff=False)
m_menu.add_cascade(label="Run", menu=r_menu)
r_menu.add_command(label="Run Python", command=run_code)

# Line count label at the bottom
line_count_label = Label(root, text="Line: 1", bd=1, relief=SUNKEN, anchor=W)
line_count_label.pack(fill=X, side=BOTTOM)

# Bind keyboard shortcuts
root.bind("<Control-Key-x>", cut_text)
root.bind("<Control-Key-c>", copy_text)
root.bind("<Control-Key-v>", paste_text)
root.bind('<Control-Key-A>', select_all)
root.bind('<Control-Key-a>', select_all)
root.bind("<Control-Key-s>", save_file)

# Start main loop
root.mainloop()
