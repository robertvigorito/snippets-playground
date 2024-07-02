"""Lets create a table view with a model and a delegate.
"""
import sys
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets


class AssetTable(QtWidgets.QTableView):
    def __init__(self, parent: Optional[object] = None) -> None:
        super().__init__(parent)



# Create a linedit search bar
class SearchBar(QtWidgets.QWidget):
    def __init__(self, parent: Optional[object] = None) -> None:
        super().__init__(parent)

        # Create a label
        label = QtWidgets.QLabel("Search:")
        # Create a line edit
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("Refine your search with machine language syntax")

        # Create a layout
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(label, 0, 0)
        grid_layout.addWidget(line_edit, 0, 1)
        self.setLayout(grid_layout)        



# Create the application
class Explorer(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Explorer")
        self.resize(800, 600)

        # Setting important flags
        # Set the window above all other windows
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)


        grid_layout = QtWidgets.QVBoxLayout()
        # grid_layout.addWidget(self.table)

        self.setLayout(grid_layout)

        # Create a search bar
        search_bar = SearchBar()
        grid_layout.addWidget(search_bar)
        self.settings = QtCore.QSettings("YourOrganization", "YourApplication")
        self.restoreGeometry(self.settings.value("windowGeometry"))

        # Enable the clear button

    # Set the current window state when the window is closed in Qsettings
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:

        self.settings.setValue("windowGeometry", self.saveGeometry())
        event.accept()



        # central_widget = QtWidgets.QWidget()
        # central_widget.setLayout(grid_layout)
    def moveEvent(self, event: QtGui.QMoveEvent) -> None:
        print(self.pos())


# Close any floating process that were not close related to the application

import subprocess

# subprocess.run(["killall", "python", "-9"])

app = QtWidgets.QApplication(sys.argv)
window = Explorer()
window.show()
sys.exit(app.exec())