import os
import sys
import requests
import shutil
import json
import tkinter as tk
import sqlite3
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import time

class BG3DialogueFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BG3 Dialogue Finder v1.0")
        self.root.geometry("800x700")
        self.root.minsize(800, 700)
        
        # Set icon if available
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Database path
        if getattr(sys, 'frozen', False):
            self.db_path = os.path.join(sys._MEIPASS, "database.db")
        else:
            self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
        
        # Config file path (stored in user's home directory)
        self.config_file = os.path.join(os.path.expanduser("~"), ".bg3_dialogue_finder_config.json")
        
        # Variables
        self.search_term_1 = tk.StringVar()
        self.search_by_1 = tk.StringVar(value="dialogue")
        self.search_term_2 = tk.StringVar()
        self.search_by_2 = tk.StringVar(value="character")
        self.search_term_3 = tk.StringVar()
        self.search_by_3 = tk.StringVar(value="type")
        # For multiple source folders, store full paths here
        self.source_folders = []  
        # Destination folder: _destination_folder_actual stores the full path while
        # destination_folder (a StringVar) holds the masked version for display.
        self._destination_folder_actual = ""
        self.destination_folder = tk.StringVar()
        self.search_results = []
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0.0)
        
        # Sorting variables
        self.sort_column = None
        self.sort_reverse = False
        
        # Create UI
        self.create_ui()
        
        # Create context menu for copying
        self.create_context_menu()

        # Load previously saved folder paths (if any)
        self.load_config()
    
    def mask_user_profile_path(self, path):
        """Replaces the current user's home folder with %USERPROFILE% for display."""
        user_home = os.path.expanduser("~")
        if path.startswith(user_home):
            return path.replace(user_home, "%USERPROFILE%", 1)
        return path
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="BG3 Dialogue Finder v1.0", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search row 1
        row1_frame = ttk.Frame(search_frame)
        row1_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1_frame, text="Search 1:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row1_frame, textvariable=self.search_term_1, width=30).pack(side=tk.LEFT, padx=(0, 5))
        
        search_by_1_combo = ttk.Combobox(row1_frame, textvariable=self.search_by_1, width=20)
        search_by_1_combo['values'] = ('dialogue', 'character', 'type', 'filename')
        search_by_1_combo.pack(side=tk.LEFT)
        
        # Search row 2
        row2_frame = ttk.Frame(search_frame)
        row2_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2_frame, text="Search 2:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row2_frame, textvariable=self.search_term_2, width=30).pack(side=tk.LEFT, padx=(0, 5))
        
        search_by_2_combo = ttk.Combobox(row2_frame, textvariable=self.search_by_2, width=20)
        search_by_2_combo['values'] = ('character', 'dialogue', 'type', 'filename')
        search_by_2_combo.pack(side=tk.LEFT)
        
        # Search row 3
        row3_frame = ttk.Frame(search_frame)
        row3_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(row3_frame, text="Search 3:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row3_frame, textvariable=self.search_term_3, width=30).pack(side=tk.LEFT, padx=(0, 5))
        
        search_by_3_combo = ttk.Combobox(row3_frame, textvariable=self.search_by_3, width=20)
        search_by_3_combo['values'] = ('type', 'dialogue', 'character', 'filename')
        search_by_3_combo.pack(side=tk.LEFT)
        
        # Folder selection frame
        folder_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source folders frame (for multiple input paths)
        source_frame = ttk.LabelFrame(folder_frame, text="Source Folders", padding="10")
        source_frame.pack(fill=tk.X, pady=5)
        
        # Listbox to display source folders (displayed as masked paths)
        self.source_listbox = tk.Listbox(source_frame, height=4)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        
        # Scrollbar for listbox
        source_scrollbar = ttk.Scrollbar(source_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        self.source_listbox.configure(yscrollcommand=source_scrollbar.set)
        source_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Buttons for managing source folders
        buttons_frame = ttk.Frame(source_frame)
        buttons_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Add", command=self.add_source_folder).pack(fill=tk.X, pady=(0,5))
        ttk.Button(buttons_frame, text="Remove", command=self.remove_source_folder).pack(fill=tk.X)
        
        # Destination folder row
        dest_frame = ttk.Frame(folder_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="Destination Folder:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(dest_frame, textvariable=self.destination_folder, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(dest_frame, text="Browse...", command=self.browse_destination).pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_button = ttk.Button(button_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_button = ttk.Button(button_frame, text="Copy Files", command=self.copy_files)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_selected_button = ttk.Button(button_frame, text="Copy Selected", command=self.copy_selected_row)
        self.copy_selected_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, 
                                           length=100, mode='determinate', 
                                           variable=self.progress_value)
        self.progress_bar.pack(fill=tk.X)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for results
        columns = ('filename', 'dialogue', 'character', 'type', 'status')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', selectmode='extended')
        
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda _col=col: self.sort_treeview(_col))
        
        self.tree.column('filename', width=150)
        self.tree.column('dialogue', width=250)
        self.tree.column('character', width=120)
        self.tree.column('type', width=120)
        self.tree.column('status', width=80)
        
        scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        status_bar = ttk.Label(self.root, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.loading_frame = ttk.Frame(self.root)
        self.loading_label = ttk.Label(self.loading_frame, text="Processing...", font=("Arial", 12))
        self.loading_label.pack(pady=10)
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy Filename", command=lambda: self.copy_cell_value('filename'))
        self.context_menu.add_command(label="Copy Dialogue", command=lambda: self.copy_cell_value('dialogue'))
        self.context_menu.add_command(label="Copy Character", command=lambda: self.copy_cell_value('character'))
        self.context_menu.add_command(label="Copy Type", command=lambda: self.copy_cell_value('type'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Row", command=self.copy_selected_row)
        self.context_menu.add_command(label="Copy All Selected Rows", command=self.copy_all_selected_rows)
    
    def show_context_menu(self, event):
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_cell_value(self, column):
        selected_item = self.tree.selection()[0]
        cell_value = self.tree.item(selected_item, 'values')[self.tree['columns'].index(column)]
        self.root.clipboard_clear()
        self.root.clipboard_append(cell_value)
        self.status_text.set(f"Copied {column}: {cell_value}")
    
    def copy_selected_row(self):
        if not self.tree.selection():
            messagebox.showinfo("Info", "No row selected")
            return
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, 'values')
        row_text = f"Filename: {values[0]}\nDialogue: {values[1]}\nCharacter: {values[2]}\nType: {values[3]}\nStatus: {values[4]}"
        self.root.clipboard_clear()
        self.root.clipboard_append(row_text)
        self.status_text.set("Copied selected row to clipboard")
    
    def copy_all_selected_rows(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No rows selected")
            return
        all_rows_text = []
        for item in selected_items:
            values = self.tree.item(item, 'values')
            row_text = f"Filename: {values[0]}\nDialogue: {values[1]}\nCharacter: {values[2]}\nType: {values[3]}\nStatus: {values[4]}"
            all_rows_text.append(row_text)
        clipboard_text = "\n\n---\n\n".join(all_rows_text)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        self.status_text.set(f"Copied {len(selected_items)} rows to clipboard")
    
    def on_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            values = self.tree.item(item, 'values')
            info = f"Filename: {values[0]}\n\nDialogue: {values[1]}\n\nCharacter: {values[2]}\n\nType: {values[3]}\n\nStatus: {values[4]}"
            dialog = tk.Toplevel(self.root)
            dialog.title("Row Details")
            dialog.geometry("600x400")
            dialog.transient(self.root)
            dialog.grab_set()
            text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
            text.insert(tk.END, info)
            text.pack(fill=tk.BOTH, expand=True)
            text.config(state=tk.DISABLED)
            copy_frame = ttk.Frame(dialog, padding="10")
            copy_frame.pack(fill=tk.X)
            ttk.Button(copy_frame, text="Copy All", 
                      command=lambda: [self.root.clipboard_clear(), 
                                      self.root.clipboard_append(info), 
                                      self.status_text.set("Copied row details to clipboard")]).pack(side=tk.LEFT, padx=5)
            ttk.Button(copy_frame, text="Close", 
                      command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def sort_treeview(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        items_with_values = [(item, self.tree.item(item, 'values')) for item in self.tree.get_children('')]
        col_idx = self.tree['columns'].index(column)
        items_with_values.sort(key=lambda x: x[1][col_idx], reverse=self.sort_reverse)
        for idx, (item, _) in enumerate(items_with_values):
            self.tree.move(item, '', idx)
        
        for col in self.tree['columns']:
            if col == column:
                direction = " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(col, text=f"{col.capitalize()}{direction}")
            else:
                self.tree.heading(col, text=col.capitalize())
    
    def show_loading(self):
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update_idletasks()
    
    def hide_loading(self):
        self.loading_frame.place_forget()
        self.root.update_idletasks()
    
    def add_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder and os.path.isdir(folder):
            if folder not in self.source_folders:
                self.source_folders.append(folder)
                # Insert masked version for display
                self.source_listbox.insert(tk.END, self.mask_user_profile_path(folder))
                self.save_config()
    
    def remove_source_folder(self):
        selected_indices = self.source_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No source folder selected for removal")
            return
        for index in reversed(selected_indices):
            folder_display = self.source_listbox.get(index)
            self.source_listbox.delete(index)
            # Remove the corresponding full path from our list
            for folder in self.source_folders:
                if self.mask_user_profile_path(folder) == folder_display:
                    self.source_folders.remove(folder)
                    break
        self.save_config()
    
    def browse_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder and os.path.isdir(folder):
            self._destination_folder_actual = folder
            self.destination_folder.set(self.mask_user_profile_path(folder))
            self.save_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.source_folders = config.get("source_folders", [])
                    dest = config.get("destination_folder", "")
                    self._destination_folder_actual = dest
                    self.destination_folder.set(self.mask_user_profile_path(dest))
                    # Update the source folders listbox with masked paths
                    self.source_listbox.delete(0, tk.END)
                    for folder in self.source_folders:
                        self.source_listbox.insert(tk.END, self.mask_user_profile_path(folder))
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to load config: {str(e)}")
    
    def save_config(self):
        config = {
            "source_folders": self.source_folders,
            "destination_folder": self._destination_folder_actual
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to save config: {str(e)}")
    
    def search(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.search_results = []
        self.status_text.set("Searching...")
        self.progress_value.set(0)
        
        self.sort_column = None
        self.sort_reverse = False
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.capitalize())
        
        self.search_button.configure(state=tk.DISABLED)
        self.copy_button.configure(state=tk.DISABLED)
        self.copy_selected_button.configure(state=tk.DISABLED)
        
        self.show_loading()
        self.root.update_idletasks()
        
        Thread(target=self._search_thread).start()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _search_thread(self):
        try:
            search_term_1 = self.search_term_1.get()
            search_by_1 = self.search_by_1.get()
            search_term_2 = self.search_term_2.get()
            search_by_2 = self.search_by_2.get()
            search_term_3 = self.search_term_3.get()
            search_by_3 = self.search_by_3.get()
            
            conditions = []
            params = []
            if search_term_1:
                conditions.append(f"{search_by_1} LIKE ?")
                params.append(f"%{search_term_1}%")
            if search_term_2:
                conditions.append(f"{search_by_2} LIKE ?")
                params.append(f"%{search_term_2}%")
            if search_term_3:
                conditions.append(f"{search_by_3} LIKE ?")
                params.append(f"%{search_term_3}%")    
            query = "SELECT * FROM filename"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                self.search_results = []
                for row in results:
                    self.search_results.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'dialogue': row['dialogue'] if (row['dialogue'] is not None and row['dialogue'].strip() != '') else 'Unknown',
                        'character': row['character'] if (row['character'] is not None and row['character'].strip() != '') else 'Unknown',
                        'type': row['type'] if (row['type'] is not None and row['type'].strip() != '') else 'Unknown',
                    })
                conn.close()
                self.root.after(0, self._update_results)
            except sqlite3.Error as e:
                self.root.after(0, lambda: messagebox.showerror("Database Error", f"Database query failed: {str(e)}"))
                self.root.after(0, lambda: self.status_text.set("Search failed"))
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.copy_selected_button.configure(state=tk.NORMAL))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set("Search failed"))
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_selected_button.configure(state=tk.NORMAL))
    
    def _update_results(self):
        for result in self.search_results:
            self.tree.insert('', tk.END, values=(
                result.get('filename', ''),
                result.get('dialogue', 'Unknown'),
                result.get('character', 'Unknown'),
                result.get('type', 'Unknown'),
                "Pending"
            ))
        self.status_text.set(f"Found {len(self.search_results)} results")
        self.hide_loading()
        self.search_button.configure(state=tk.NORMAL)
        self.copy_button.configure(state=tk.NORMAL)
        self.copy_selected_button.configure(state=tk.NORMAL)
    
    def copy_files(self):
        if not self.search_results:
            messagebox.showinfo("Info", "No search results to copy")
            return
        
        # Use all added source folders (full paths stored in self.source_folders)
        sources = self.source_folders
        # Use the actual full destination folder (not the masked version)
        destination = self._destination_folder_actual
        
        if not sources:
            messagebox.showerror("Error", "Please add at least one valid source folder")
            return
        
        for folder in sources:
            if not os.path.isdir(folder):
                messagebox.showerror("Error", f"Source folder does not exist: {folder}")
                return
        
        if not destination or not os.path.isdir(destination):
            messagebox.showerror("Error", "Please select a valid destination folder")
            return
        
        self.search_button.configure(state=tk.DISABLED)
        self.copy_button.configure(state=tk.DISABLED)
        self.copy_selected_button.configure(state=tk.DISABLED)
        
        self.progress_value.set(0)
        for item in self.tree.get_children():
            self.tree.set(item, 'status', "Pending")
        
        self.status_text.set("Preparing to copy files...")
        self.root.update_idletasks()
        
        Thread(target=self._copy_thread, args=(sources, destination)).start()
    
    def _copy_thread(self, sources, destination):
        self.root.after(0, lambda: self.status_text.set("Scanning source folders for files..."))
        copied = 0
        not_found = 0
        total_files = len(self.search_results)
        try:
            self.root.after(0, lambda: self.status_text.set("Building file index..."))
            file_index = {}
            file_count = 0
            for folder in sources:
                for root_dir, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith('.wem'):
                            file_index[file] = root_dir
                            file_count += 1
                            if file_count % 1000 == 0:
                                self.root.after(0, lambda: self.status_text.set(f"Indexed {file_count} files..."))
            self.root.after(0, lambda: self.status_text.set(f"Found {file_count} .wem files in source folders. Starting copy..."))
            for i, result in enumerate(self.search_results):
                filename = result.get('filename', '')
                if not filename:
                    continue
                base_filename = os.path.basename(filename)
                self.root.after(0, lambda i=i, base_filename=base_filename: self.status_text.set(f"Processing {i+1}/{total_files}: {base_filename}"))
                progress_percent = (i / total_files) * 100
                self.root.after(0, lambda: self.progress_value.set(progress_percent))
                item_id = self.tree.get_children()[i]
                if base_filename in file_index:
                    source_path = os.path.join(file_index[base_filename], base_filename)
                    dest_path = os.path.join(destination, base_filename)
                    shutil.copy2(source_path, dest_path)
                    copied += 1
                    self.root.after(0, lambda id=item_id: self.tree.set(id, 'status', "Copied"))
                    self.root.after(0, lambda id=item_id: self.tree.item(id, tags=('copied',)))
                else:
                    not_found += 1
                    self.root.after(0, lambda id=item_id: self.tree.set(id, 'status', "Not Found"))
                    self.root.after(0, lambda id=item_id: self.tree.item(id, tags=('not_found',)))
                time.sleep(0.01)
            self.root.after(0, lambda: self.progress_value.set(100))
            message = f"Copied {copied} files. {not_found} files were not found."
            self.root.after(0, lambda: messagebox.showinfo("Copy Complete", message))
            self.root.after(0, lambda: self.status_text.set(f"Copied {copied} files. {not_found} files not found."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Copy failed: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set("Copy failed"))
        finally:
            self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_selected_button.configure(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10))
    style.map('Treeview', 
              foreground=[('disabled', 'gray')],
              background=[('selected', '#0078D7')])
    
    app = BG3DialogueFinderApp(root)
    
    app.tree.tag_configure('copied', background='#E6FFE6')
    app.tree.tag_configure('not_found', background='#FFE6E6')
    
    root.mainloop()
