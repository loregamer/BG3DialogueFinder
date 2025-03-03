import os
import sys
import json
import sqlite3
import shutil
import time

from PyQt6 import QtCore, QtWidgets, QtGui
import qtawesome as qta

# Worker for running the database search in a separate thread
class SearchWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    error = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(str)
    
    def __init__(self, db_path, search_params):
        super().__init__()
        self.db_path = db_path
        self.search_params = search_params  # dict with keys: term1, by1, term2, by2, term3, by3

    def run(self):
        try:
            term1 = self.search_params.get("term1", "")
            by1 = self.search_params.get("by1", "dialogue")
            term2 = self.search_params.get("term2", "")
            by2 = self.search_params.get("by2", "character")
            term3 = self.search_params.get("term3", "")
            by3 = self.search_params.get("by3", "type")
            
            conditions = []
            params = []
            if term1:
                conditions.append(f"{by1} LIKE ?")
                params.append(f"%{term1}%")
            if term2:
                conditions.append(f"{by2} LIKE ?")
                params.append(f"%{term2}%")
            if term3:
                conditions.append(f"{by3} LIKE ?")
                params.append(f"%{term3}%")
            
            query = "SELECT * FROM filename"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Build list of dictionaries similar to the original code
            search_results = []
            for row in results:
                search_results.append({
                    'id': row['id'],
                    'filename': row['filename'],
                    'dialogue': row['dialogue'].strip() if row['dialogue'] and row['dialogue'].strip() else 'Unknown',
                    'character': row['character'].strip() if row['character'] and row['character'].strip() else 'Unknown',
                    'type': row['type'].strip() if row['type'] and row['type'].strip() else 'Unknown',
                })
            self.finished.emit(search_results)
        except Exception as e:
            self.error.emit(str(e))

# Worker for copying files (runs in a separate thread)
class CopyWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int)  # progress percent
    status_update = QtCore.pyqtSignal(str)
    
    def __init__(self, sources, destination, search_results):
        super().__init__()
        self.sources = sources
        self.destination = destination
        self.search_results = search_results

    def run(self):
        try:
            self.status_update.emit("Building file index...")
            file_index = {}
            file_count = 0
            # Scan each source folder for .wem files
            for folder in self.sources:
                for root_dir, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith('.wem'):
                            file_index[file] = root_dir
                            file_count += 1
            self.status_update.emit(f"Found {file_count} .wem files. Starting copy...")
            
            copied = 0
            not_found = 0
            total = len(self.search_results)
            for i, result in enumerate(self.search_results):
                filename = result.get('filename', '')
                if not filename:
                    continue
                base_filename = os.path.basename(filename)
                self.status_update.emit(f"Processing {i+1}/{total}: {base_filename}")
                progress_percent = int((i / total) * 100)
                self.progress.emit(progress_percent)
                if base_filename in file_index:
                    src_path = os.path.join(file_index[base_filename], base_filename)
                    dest_path = os.path.join(self.destination, base_filename)
                    shutil.copy2(src_path, dest_path)
                    copied += 1
                else:
                    not_found += 1
                time.sleep(0.01)  # Small delay for UI updates
            self.progress.emit(100)
            self.finished.emit(f"Copied {copied} files. {not_found} files not found.")
        except Exception as e:
            self.finished.emit(f"Copy failed: {str(e)}")


# Main application window using PyQt6
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BG3 Dialogue Finder v1.0")
        self.resize(800, 700)
        
        # Full paths for database and config
        if getattr(sys, 'frozen', False):
            self.app_path = sys._MEIPASS
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.app_path, "database.db")
        self.config_file = os.path.join(os.path.expanduser("~"), ".bg3_dialogue_finder_config.json")
        
        # Internal storage for folder paths (full paths)
        self.source_folders = []  # list of full paths
        self._destination_folder_actual = ""
        
        self.search_results = []
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        
        # --- Search parameters ---
        search_group = QtWidgets.QGroupBox("Search Parameters")
        main_layout.addWidget(search_group)
        search_layout = QtWidgets.QGridLayout(search_group)
        
        self.search_term1 = QtWidgets.QLineEdit()
        self.search_by1 = QtWidgets.QComboBox()
        self.search_by1.addItems(["dialogue", "character", "type", "filename"])
        self.search_term2 = QtWidgets.QLineEdit()
        self.search_by2 = QtWidgets.QComboBox()
        self.search_by2.addItems(["character", "dialogue", "type", "filename"])
        self.search_term3 = QtWidgets.QLineEdit()
        self.search_by3 = QtWidgets.QComboBox()
        self.search_by3.addItems(["type", "dialogue", "character", "filename"])
        
        search_layout.addWidget(QtWidgets.QLabel("Search 1:"), 0, 0)
        search_layout.addWidget(self.search_term1, 0, 1)
        search_layout.addWidget(self.search_by1, 0, 2)
        
        search_layout.addWidget(QtWidgets.QLabel("Search 2:"), 1, 0)
        search_layout.addWidget(self.search_term2, 1, 1)
        search_layout.addWidget(self.search_by2, 1, 2)
        
        search_layout.addWidget(QtWidgets.QLabel("Search 3:"), 2, 0)
        search_layout.addWidget(self.search_term3, 2, 1)
        search_layout.addWidget(self.search_by3, 2, 2)
        
        # --- Folder selection ---
        folder_group = QtWidgets.QGroupBox("Folder Selection")
        main_layout.addWidget(folder_group)
        folder_layout = QtWidgets.QGridLayout(folder_group)
        
        # Source folders (using QListWidget with inline editing enabled)
        source_label = QtWidgets.QLabel("Source Folders:")
        folder_layout.addWidget(source_label, 0, 0)
        self.source_list = QtWidgets.QListWidget()
        self.source_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked |
                                         QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        folder_layout.addWidget(self.source_list, 0, 1)
        
        btn_add = QtWidgets.QPushButton(qta.icon('fa5s.plus'), "Add")
        btn_add.clicked.connect(self.add_source_folder)
        btn_remove = QtWidgets.QPushButton(qta.icon('fa5s.minus'), "Remove")
        btn_remove.clicked.connect(self.remove_source_folder)
        btns_layout = QtWidgets.QVBoxLayout()
        btns_layout.addWidget(btn_add)
        btns_layout.addWidget(btn_remove)
        folder_layout.addLayout(btns_layout, 0, 2)
        
        # Destination folder
        dest_label = QtWidgets.QLabel("Destination Folder:")
        folder_layout.addWidget(dest_label, 1, 0)
        self.dest_edit = QtWidgets.QLineEdit()
        self.dest_edit.editingFinished.connect(self.on_dest_edit_finished)
        folder_layout.addWidget(self.dest_edit, 1, 1)
        btn_browse_dest = QtWidgets.QPushButton(qta.icon('fa5s.folder-open'), "Browse...")
        btn_browse_dest.clicked.connect(self.browse_destination)
        folder_layout.addWidget(btn_browse_dest, 1, 2)
        
        # --- Buttons for Search/Copy ---
        buttons_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        self.btn_search = QtWidgets.QPushButton(qta.icon('fa5s.search'), "Search")
        self.btn_search.clicked.connect(self.search)
        buttons_layout.addWidget(self.btn_search)
        
        self.btn_copy = QtWidgets.QPushButton(qta.icon('fa5s.copy'), "Copy Files")
        self.btn_copy.clicked.connect(self.copy_files)
        buttons_layout.addWidget(self.btn_copy)
        
        self.btn_copy_sel = QtWidgets.QPushButton(qta.icon('fa5s.clipboard'), "Copy Selected")
        # You can add a slot for copy-selected functionality here.
        buttons_layout.addWidget(self.btn_copy_sel)
        
        # --- Progress Bar ---
        self.progress_bar = QtWidgets.QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # --- Table for search results ---
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Filename", "Dialogue", "Character", "Type", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)
        
        # --- Status Bar ---
        self.statusBar().showMessage("Ready")
        
        # Connect source list item changes (for manual edits)
        self.source_list.itemChanged.connect(self.on_source_item_changed)
    
    # Helper functions for masking/unmasking paths
    def mask_user_profile_path(self, path):
        user_home = os.path.normpath(os.path.expanduser("~"))
        norm_path = os.path.normpath(path)
        if norm_path.lower().startswith(user_home.lower()):
            return "%USERPROFILE%" + norm_path[len(user_home):]
        return norm_path

    def unmask_user_profile_path(self, text):
        if text.startswith("%USERPROFILE%"):
            user_home = os.path.normpath(os.path.expanduser("~"))
            return os.path.join(user_home, text[len("%USERPROFILE%"):].lstrip(os.sep))
        return os.path.normpath(text)
    
    # --- Slots for folder fields ---
    def add_source_folder(self):
        # Let the user either type manually or select using a dialog.
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            if folder not in self.source_folders:
                self.source_folders.append(folder)
                masked = self.mask_user_profile_path(folder)
                item = QtWidgets.QListWidgetItem(masked)
                item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                self.source_list.addItem(item)
                self.save_config()
    
    def remove_source_folder(self):
        for item in self.source_list.selectedItems():
            row = self.source_list.row(item)
            masked = item.text()
            # Remove from internal list by comparing masked values
            for folder in self.source_folders:
                if self.mask_user_profile_path(folder) == masked:
                    self.source_folders.remove(folder)
                    break
            self.source_list.takeItem(row)
        self.save_config()
    
    def on_source_item_changed(self, item):
        # When a source folder item is edited, unmask then mask again.
        new_text = item.text()
        full_path = self.unmask_user_profile_path(new_text)
        # Update internal list by finding the corresponding masked version and replacing it.
        for i, folder in enumerate(self.source_folders):
            if self.mask_user_profile_path(folder) == new_text:
                self.source_folders[i] = full_path
                break
        # Reset the item text to the masked version.
        item.setText(self.mask_user_profile_path(full_path))
        self.save_config()
    
    def browse_destination(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self._destination_folder_actual = folder
            self.dest_edit.setText(self.mask_user_profile_path(folder))
            self.save_config()
    
    def on_dest_edit_finished(self):
        # When editing is finished, update the destination text.
        text = self.dest_edit.text()
        full_path = self.unmask_user_profile_path(text)
        self._destination_folder_actual = full_path
        self.dest_edit.setText(self.mask_user_profile_path(full_path))
        self.save_config()
    
    # --- Config persistence ---
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                self.source_folders = config.get("source_folders", [])
                dest = config.get("destination_folder", "")
                self._destination_folder_actual = dest
                self.dest_edit.setText(self.mask_user_profile_path(dest))
                # Update source list widget
                self.source_list.clear()
                for folder in self.source_folders:
                    masked = self.mask_user_profile_path(folder)
                    item = QtWidgets.QListWidgetItem(masked)
                    item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                    self.source_list.addItem(item)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Warning", f"Failed to load config: {str(e)}")
    
    def save_config(self):
        config = {
            "source_folders": self.source_folders,
            "destination_folder": self._destination_folder_actual
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Warning", f"Failed to save config: {str(e)}")
    
    # --- Search and Copy actions ---
    def search(self):
        # Disable buttons while searching
        self.btn_search.setEnabled(False)
        self.statusBar().showMessage("Searching...")
        # Clear table
        self.table.setRowCount(0)
        # Gather search parameters
        params = {
            "term1": self.search_term1.text(),
            "by1": self.search_by1.currentText(),
            "term2": self.search_term2.text(),
            "by2": self.search_by2.currentText(),
            "term3": self.search_term3.text(),
            "by3": self.search_by3.currentText(),
        }
        # Create the search worker and thread
        self.search_thread = QtCore.QThread()
        self.search_worker = SearchWorker(self.db_path, params)
        self.search_worker.moveToThread(self.search_thread)
        self.search_thread.started.connect(self.search_worker.run)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.finished.connect(lambda: self.search_thread.quit())
        self.search_worker.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)
        self.search_thread.start()
    
    def on_search_finished(self, results):
        self.search_results = results
        # Populate table
        self.table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(result.get('filename', '')))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(result.get('dialogue', 'Unknown')))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(result.get('character', 'Unknown')))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(result.get('type', 'Unknown')))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem("Pending"))
        self.statusBar().showMessage(f"Found {len(results)} results")
        self.btn_search.setEnabled(True)
    
    def on_search_error(self, error_msg):
        QtWidgets.QMessageBox.critical(self, "Search Error", error_msg)
        self.statusBar().showMessage("Search failed")
        self.btn_search.setEnabled(True)
    
    def copy_files(self):
        # Check if there are search results and valid folders
        if not self.search_results:
            QtWidgets.QMessageBox.information(self, "Info", "No search results to copy")
            return
        if not self.source_folders:
            QtWidgets.QMessageBox.critical(self, "Error", "Please add at least one valid source folder")
            return
        if not self._destination_folder_actual or not os.path.isdir(self._destination_folder_actual):
            QtWidgets.QMessageBox.critical(self, "Error", "Please select a valid destination folder")
            return
        
        self.btn_copy.setEnabled(False)
        self.statusBar().showMessage("Copying files...")
        self.progress_bar.setValue(0)
        
        # Create the copy worker and thread
        self.copy_thread = QtCore.QThread()
        self.copy_worker = CopyWorker(self.source_folders, self._destination_folder_actual, self.search_results)
        self.copy_worker.moveToThread(self.copy_thread)
        self.copy_thread.started.connect(self.copy_worker.run)
        self.copy_worker.progress.connect(self.progress_bar.setValue)
        self.copy_worker.status_update.connect(lambda msg: self.statusBar().showMessage(msg))
        self.copy_worker.finished.connect(self.on_copy_finished)
        self.copy_worker.finished.connect(lambda: self.copy_thread.quit())
        self.copy_worker.finished.connect(self.copy_worker.deleteLater)
        self.copy_thread.finished.connect(self.copy_thread.deleteLater)
        self.copy_thread.start()
    
    def on_copy_finished(self, message):
        QtWidgets.QMessageBox.information(self, "Copy Complete", message)
        self.statusBar().showMessage(message)
        self.btn_copy.setEnabled(True)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
