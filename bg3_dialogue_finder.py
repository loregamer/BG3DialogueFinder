import os
import sys
import time
import shutil
import requests
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QFileDialog,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QMessageBox, QSplashScreen
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

# -------------------- Worker Threads --------------------

class SearchWorker(QThread):
    resultsReady = pyqtSignal(list)
    errorOccurred = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            response = requests.post(
                "https://nocomplydev.pythonanywhere.com/multi_search",
                headers={
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://nocomplydev.pythonanywhere.com",
                    "Referer": "https://nocomplydev.pythonanywhere.com/",
                    "User-Agent": "Mozilla/5.0"
                },
                data=self.params
            )
            if response.status_code == 200:
                results = response.json()
                self.resultsReady.emit(results)
            else:
                self.errorOccurred.emit(f"API request failed with status code {response.status_code}")
        except Exception as e:
            self.errorOccurred.emit(str(e))


class CopyWorker(QThread):
    progressUpdated = pyqtSignal(int)  # Emits percentage (0-100)
    fileStatusUpdated = pyqtSignal(int, str)  # row index, status text
    finishedCopy = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(self, search_results, source, destination):
        super().__init__()
        self.search_results = search_results
        self.source = source
        self.destination = destination

    def run(self):
        total_files = len(self.search_results)
        try:
            # Build file index: scan source folder for .wem files
            file_index = {}
            for root, _, files in os.walk(self.source):
                for file in files:
                    if file.lower().endswith('.wem'):
                        file_index[file] = os.path.join(root, file)
            copied = 0
            not_found = 0
            for i, result in enumerate(self.search_results):
                filename = result.get('filename', '')
                base_filename = os.path.basename(filename)
                if base_filename in file_index:
                    src_path = file_index[base_filename]
                    dst_path = os.path.join(self.destination, base_filename)
                    shutil.copy2(src_path, dst_path)
                    copied += 1
                    self.fileStatusUpdated.emit(i, "Copied")
                else:
                    not_found += 1
                    self.fileStatusUpdated.emit(i, "Not Found")
                progress_percent = int(((i + 1) / total_files) * 100)
                self.progressUpdated.emit(progress_percent)
                time.sleep(0.01)
            message = f"Copied {copied} files. {not_found} files not found."
            self.finishedCopy.emit(message)
        except Exception as e:
            self.errorOccurred.emit(str(e))


# -------------------- Main Application Window --------------------

class BG3DialogueFinderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BG3 Dialogue Finder")
        self.setMinimumSize(800, 700)
        self.search_results = []

        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.initUI()

    def initUI(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)

        # Title label
        title = QLabel("BG3 Dialogue Finder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title)

        # --- Search Parameters ---
        searchGroup = QGroupBox("Search Parameters")
        searchLayout = QVBoxLayout(searchGroup)

        # Row 1
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Search 1:"))
        self.searchTerm1 = QLineEdit()
        row1.addWidget(self.searchTerm1)
        self.searchBy1 = QComboBox()
        self.searchBy1.addItems(["dialogue", "character", "type", "filename"])
        row1.addWidget(self.searchBy1)
        searchLayout.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Search 2:"))
        self.searchTerm2 = QLineEdit()
        row2.addWidget(self.searchTerm2)
        self.searchBy2 = QComboBox()
        self.searchBy2.addItems(["character", "dialogue", "type", "filename"])
        row2.addWidget(self.searchBy2)
        searchLayout.addLayout(row2)

        # Row 3
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Search 3:"))
        self.searchTerm3 = QLineEdit()
        row3.addWidget(self.searchTerm3)
        self.searchBy3 = QComboBox()
        self.searchBy3.addItems(["type", "dialogue", "character", "filename"])
        row3.addWidget(self.searchBy3)
        searchLayout.addLayout(row3)

        main_layout.addWidget(searchGroup)

        # --- Folder Selection ---
        folderGroup = QGroupBox("Folder Selection")
        folderLayout = QVBoxLayout(folderGroup)
        # Source Folder
        srcLayout = QHBoxLayout()
        srcLayout.addWidget(QLabel("Source Folder:"))
        self.sourceFolderEdit = QLineEdit()
        srcLayout.addWidget(self.sourceFolderEdit)
        self.browseSourceBtn = QPushButton("Browse...")
        self.browseSourceBtn.clicked.connect(self.browseSource)
        srcLayout.addWidget(self.browseSourceBtn)
        folderLayout.addLayout(srcLayout)
        # Destination Folder
        dstLayout = QHBoxLayout()
        dstLayout.addWidget(QLabel("Destination Folder:"))
        self.destFolderEdit = QLineEdit()
        dstLayout.addWidget(self.destFolderEdit)
        self.browseDestBtn = QPushButton("Browse...")
        self.browseDestBtn.clicked.connect(self.browseDestination)
        dstLayout.addWidget(self.browseDestBtn)
        folderLayout.addLayout(dstLayout)
        main_layout.addWidget(folderGroup)

        # --- Buttons ---
        btnLayout = QHBoxLayout()
        self.searchBtn = QPushButton("Search")
        self.searchBtn.clicked.connect(self.search)
        btnLayout.addWidget(self.searchBtn)
        self.copyFilesBtn = QPushButton("Copy Files")
        self.copyFilesBtn.clicked.connect(self.copyFiles)
        btnLayout.addWidget(self.copyFilesBtn)
        self.copySelectedBtn = QPushButton("Copy Selected")
        self.copySelectedBtn.clicked.connect(self.copySelected)
        btnLayout.addWidget(self.copySelectedBtn)
        main_layout.addLayout(btnLayout)

        # --- Progress Bar ---
        self.progressBar = QProgressBar()
        main_layout.addWidget(self.progressBar)

        # --- Results Table ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Filename", "Dialogue", "Character", "Type", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showContextMenu)
        main_layout.addWidget(self.table)

        # --- Status Label ---
        self.statusLabel = QLabel("Ready")
        main_layout.addWidget(self.statusLabel)

        self.setCentralWidget(central)

        # --- Apply a modern style ---
        self.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border-radius: 4px;
                background-color: #2c3e50;
                color: white;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)

    def browseSource(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.sourceFolderEdit.setText(folder)

    def browseDestination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.destFolderEdit.setText(folder)

    def search(self):
        # Clear previous results
        self.table.setRowCount(0)
        self.search_results = []
        self.statusLabel.setText("Searching...")
        self.searchBtn.setEnabled(False)
        self.copyFilesBtn.setEnabled(False)
        self.copySelectedBtn.setEnabled(False)

        params = {
            'search_term_1': self.searchTerm1.text(),
            'search_by_1': self.searchBy1.currentText(),
            'search_term_2': self.searchTerm2.text(),
            'search_by_2': self.searchBy2.currentText(),
            'search_term_3': self.searchTerm3.text(),
            'search_by_3': self.searchBy3.currentText()
        }

        self.searchWorker = SearchWorker(params)
        self.searchWorker.resultsReady.connect(self.handleSearchResults)
        self.searchWorker.errorOccurred.connect(self.handleSearchError)
        self.searchWorker.start()

    def handleSearchResults(self, results):
        self.search_results = results
        self.table.setRowCount(len(results))
        for i, result in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(result.get('filename', '')))
            self.table.setItem(i, 1, QTableWidgetItem(result.get('dialogue', 'Unknown')))
            self.table.setItem(i, 2, QTableWidgetItem(result.get('character', 'Unknown')))
            self.table.setItem(i, 3, QTableWidgetItem(result.get('type', 'Unknown')))
            self.table.setItem(i, 4, QTableWidgetItem("Pending"))
        self.statusLabel.setText(f"Found {len(results)} results")
        self.searchBtn.setEnabled(True)
        self.copyFilesBtn.setEnabled(True)
        self.copySelectedBtn.setEnabled(True)

    def handleSearchError(self, error):
        QMessageBox.critical(self, "Error", f"Search failed: {error}")
        self.statusLabel.setText("Search failed")
        self.searchBtn.setEnabled(True)
        self.copyFilesBtn.setEnabled(True)
        self.copySelectedBtn.setEnabled(True)

    def copyFiles(self):
        if not self.search_results:
            QMessageBox.information(self, "Info", "No search results to copy")
            return

        source = self.sourceFolderEdit.text()
        destination = self.destFolderEdit.text()
        if not source or not os.path.isdir(source):
            QMessageBox.critical(self, "Error", "Please select a valid source folder")
            return
        if not destination or not os.path.isdir(destination):
            QMessageBox.critical(self, "Error", "Please select a valid destination folder")
            return

        self.searchBtn.setEnabled(False)
        self.copyFilesBtn.setEnabled(False)
        self.copySelectedBtn.setEnabled(False)
        self.statusLabel.setText("Copying files...")
        self.progressBar.setValue(0)
        # Reset status column to "Pending"
        for i in range(self.table.rowCount()):
            self.table.setItem(i, 4, QTableWidgetItem("Pending"))

        self.copyWorker = CopyWorker(self.search_results, source, destination)
        self.copyWorker.progressUpdated.connect(self.progressBar.setValue)
        self.copyWorker.fileStatusUpdated.connect(self.updateTableStatus)
        self.copyWorker.finishedCopy.connect(self.copyFinished)
        self.copyWorker.errorOccurred.connect(lambda e: QMessageBox.critical(self, "Error", f"Copy failed: {e}"))
        self.copyWorker.start()

    def updateTableStatus(self, row, status):
        if row < self.table.rowCount():
            self.table.setItem(row, 4, QTableWidgetItem(status))

    def copyFinished(self, message):
        self.statusLabel.setText(message)
        QMessageBox.information(self, "Copy Complete", message)
        self.searchBtn.setEnabled(True)
        self.copyFilesBtn.setEnabled(True)
        self.copySelectedBtn.setEnabled(True)

    def copySelected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Info", "No row selected")
            return
        rows = {}
        for item in selected:
            row = item.row()
            if row not in rows:
                rows[row] = []
            rows[row].append(self.table.item(row, 0).text())
            rows[row].append(self.table.item(row, 1).text())
            rows[row].append(self.table.item(row, 2).text())
            rows[row].append(self.table.item(row, 3).text())
            rows[row].append(self.table.item(row, 4).text())
        clipboard_text = ""
        for r in rows.values():
            clipboard_text += (f"Filename: {r[0]}\nDialogue: {r[1]}\n"
                               f"Character: {r[2]}\nType: {r[3]}\nStatus: {r[4]}\n\n---\n\n")
        QApplication.clipboard().setText(clipboard_text)
        self.statusLabel.setText("Copied selected row(s) to clipboard")

    def showContextMenu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        menu = QMenu()
        menu.addAction("Copy Filename", lambda: self.copyCell("Filename"))
        menu.addAction("Copy Dialogue", lambda: self.copyCell("Dialogue"))
        menu.addAction("Copy Character", lambda: self.copyCell("Character"))
        menu.addAction("Copy Type", lambda: self.copyCell("Type"))
        menu.addSeparator()
        menu.addAction("Copy Row", self.copySelected)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def copyCell(self, columnName):
        col = {"Filename": 0, "Dialogue": 1, "Character": 2, "Type": 3}.get(columnName, 0)
        selected = self.table.selectedItems()
        if selected:
            cell_text = selected[0].text()
            QApplication.clipboard().setText(cell_text)
            self.statusLabel.setText(f"Copied {columnName}: {cell_text}")


# -------------------- Splash Screen --------------------

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.GlobalColor.darkBlue)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMessage("Loading...", Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)


# -------------------- Main --------------------

def main():
    app = QApplication(sys.argv)
    # Optionally, set a Fusion style for a modern look
    app.setStyle("Fusion")

    splash = SplashScreen()
    splash.show()

    # Chain timer updates to mimic a splash sequence
    QTimer.singleShot(500, lambda: splash.showMessage("Initializing application...", Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white))
    QTimer.singleShot(1000, lambda: splash.showMessage("Creating resources...", Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white))
    QTimer.singleShot(1500, lambda: splash.showMessage("Setting up user interface...", Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white))
    QTimer.singleShot(2000, lambda: splash.showMessage("Ready to launch!", Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white))

    window = BG3DialogueFinderWindow()
    QTimer.singleShot(2500, lambda: splash.finish(window))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
