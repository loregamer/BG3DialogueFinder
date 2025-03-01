import os
import sys
import requests
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import time

class BG3DialogueFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BG3 Dialogue Finder")
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
        
        # Variables
        self.search_term_1 = tk.StringVar()
        self.search_by_1 = tk.StringVar(value="dialogue")
        self.search_term_2 = tk.StringVar()
        self.search_by_2 = tk.StringVar(value="character")
        self.search_term_3 = tk.StringVar()
        self.search_by_3 = tk.StringVar(value="type")
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.search_results = []
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0.0)
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="BG3 Dialogue Finder", font=("Arial", 16, "bold"))
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
        
        # Source folder row
        source_frame = ttk.Frame(folder_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="Source Folder:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(source_frame, textvariable=self.source_folder, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).pack(side=tk.LEFT)
        
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
        self.copy_button.pack(side=tk.LEFT)
        
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
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('filename', text='Filename')
        self.tree.heading('dialogue', text='Dialogue')
        self.tree.heading('character', text='Character')
        self.tree.heading('type', text='Type')
        self.tree.heading('status', text='Status')
        
        # Define columns
        self.tree.column('filename', width=150)
        self.tree.column('dialogue', width=250)
        self.tree.column('character', width=120)
        self.tree.column('type', width=120)
        self.tree.column('status', width=80)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        # Pack scrollbars and treeview
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status_bar = ttk.Label(self.root, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a loading indicator
        self.loading_frame = ttk.Frame(self.root)
        self.loading_label = ttk.Label(self.loading_frame, text="Processing...", font=("Arial", 12))
        self.loading_label.pack(pady=10)
        # Don't pack the loading frame yet - we'll show it when needed
    
    def show_loading(self):
        # Position the loading frame in the center of the window
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update_idletasks()
    
    def hide_loading(self):
        self.loading_frame.place_forget()
        self.root.update_idletasks()
    
    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
    
    def browse_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder.set(folder)
    
    def search(self):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.search_results = []
        self.status_text.set("Searching...")
        self.progress_value.set(0)
        
        # Disable buttons during search
        self.search_button.configure(state=tk.DISABLED)
        self.copy_button.configure(state=tk.DISABLED)
        
        # Show loading indicator
        self.show_loading()
        self.root.update_idletasks()
        
        # Start search in a separate thread
        Thread(target=self._search_thread).start()
    
    def _search_thread(self):
        try:
            # Prepare search parameters
            data = {
                'search_term_1': self.search_term_1.get(),
                'search_by_1': self.search_by_1.get(),
                'search_term_2': self.search_term_2.get(),
                'search_by_2': self.search_by_2.get(),
                'search_term_3': self.search_term_3.get(),
                'search_by_3': self.search_by_3.get()
            }
            
            # Make API request
            response = requests.post(
                "https://nocomplydev.pythonanywhere.com/multi_search",
                headers={
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://nocomplydev.pythonanywhere.com",
                    "Referer": "https://nocomplydev.pythonanywhere.com/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                },
                data=data
            )
            
            if response.status_code == 200:
                self.search_results = response.json()
                
                # Update UI in the main thread
                self.root.after(0, self._update_results)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"API request failed with status code {response.status_code}"))
                self.root.after(0, lambda: self.status_text.set("Search failed"))
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set("Search failed"))
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))
    
    def _update_results(self):
        # Update treeview with search results
        for result in self.search_results:
            self.tree.insert('', tk.END, values=(
                result.get('filename', ''),
                result.get('dialogue', 'Unknown'),
                result.get('character', 'Unknown'),
                result.get('type', 'Unknown'),
                "Pending"
            ))
        
        self.status_text.set(f"Found {len(self.search_results)} results")
        
        # Hide loading indicator and re-enable buttons
        self.hide_loading()
        self.search_button.configure(state=tk.NORMAL)
        self.copy_button.configure(state=tk.NORMAL)
    
    def copy_files(self):
        if not self.search_results:
            messagebox.showinfo("Info", "No search results to copy")
            return
        
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        
        if not source or not os.path.isdir(source):
            messagebox.showerror("Error", "Please select a valid source folder")
            return
        
        if not destination or not os.path.isdir(destination):
            messagebox.showerror("Error", "Please select a valid destination folder")
            return
        
        # Disable buttons during copy
        self.search_button.configure(state=tk.DISABLED)
        self.copy_button.configure(state=tk.DISABLED)
        
        # Reset progress bar
        self.progress_value.set(0)
        
        # Reset status column in treeview
        for item in self.tree.get_children():
            self.tree.set(item, 'status', "Pending")
        
        # Show loading indicator
        self.status_text.set("Preparing to copy files...")
        self.root.update_idletasks()
        
        # Start copy in a separate thread
        Thread(target=self._copy_thread, args=(source, destination)).start()
    
    def _copy_thread(self, source, destination):
        self.root.after(0, lambda: self.status_text.set("Scanning source folder for files..."))
        
        copied = 0
        not_found = 0
        total_files = len(self.search_results)
        
        try:
            # First scan the source directory to build a file index for faster lookup
            self.root.after(0, lambda: self.status_text.set("Building file index..."))
            file_index = {}
            
            # Update progress as we scan
            file_count = 0
            for root, _, files in os.walk(source):
                for file in files:
                    if file.lower().endswith('.wem'):
                        file_index[file] = root
                        file_count += 1
                        if file_count % 1000 == 0:  # Update progress periodically
                            self.root.after(0, lambda: self.status_text.set(f"Indexed {file_count} files..."))
            
            self.root.after(0, lambda: self.status_text.set(f"Found {file_count} .wem files in source folder. Starting copy..."))
            
            # Now process each search result
            for i, result in enumerate(self.search_results):
                filename = result.get('filename', '')
                if not filename:
                    continue
                
                # Extract just the filename part (without path)
                base_filename = os.path.basename(filename)
                
                # Update the current file in status
                self.root.after(0, lambda: self.status_text.set(f"Processing {i+1}/{total_files}: {base_filename}"))
                
                # Update progress bar
                progress_percent = (i / total_files) * 100
                self.root.after(0, lambda: self.progress_value.set(progress_percent))
                
                # Get the item ID in the treeview
                item_id = self.tree.get_children()[i]
                
                # Check if file exists in our index
                if base_filename in file_index:
                    source_path = os.path.join(file_index[base_filename], base_filename)
                    dest_path = os.path.join(destination, base_filename)
                    
                    # Copy the file
                    shutil.copy2(source_path, dest_path)
                    copied += 1
                    
                    # Update status in treeview
                    self.root.after(0, lambda id=item_id: self.tree.set(id, 'status', "Copied"))
                    self.root.after(0, lambda id=item_id: self.tree.item(id, tags=('copied',)))
                else:
                    not_found += 1
                    
                    # Update status in treeview
                    self.root.after(0, lambda id=item_id: self.tree.set(id, 'status', "Not Found"))
                    self.root.after(0, lambda id=item_id: self.tree.item(id, tags=('not_found',)))
                
                # Small delay to allow UI updates
                time.sleep(0.01)
            
            # Set progress to 100% when done
            self.root.after(0, lambda: self.progress_value.set(100))
            
            # Show results
            message = f"Copied {copied} files. {not_found} files were not found."
            self.root.after(0, lambda: messagebox.showinfo("Copy Complete", message))
            self.root.after(0, lambda: self.status_text.set(f"Copied {copied} files. {not_found} files not found."))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Copy failed: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set("Copy failed"))
        
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.search_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.copy_button.configure(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure style for treeview tags
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10))
    style.map('Treeview', 
              foreground=[('disabled', 'gray')],
              background=[('selected', '#0078D7')])
    
    # Create and run the app
    app = BG3DialogueFinderApp(root)
    
    # Configure tag colors for treeview
    app.tree.tag_configure('copied', background='#E6FFE6')  # Light green
    app.tree.tag_configure('not_found', background='#FFE6E6')  # Light red
    
    root.mainloop() 