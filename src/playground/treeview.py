"""Play around with creating a widget that displays a tree of items.

TODO: 
"""
from functools import partial
import sys
from typing import Optional
from PySide2 import QtCore, QtWidgets, QtGui
import PySide2.QtWidgets
            
class SearchBarLineEdit(QtWidgets.QLineEdit):
    """A line edit that has a search icon and a clear button.
    """
    
    def __init__(self) -> None:
        """Initialize the line edit with a search icon and a clear button."""
        super().__init__()
        
        # Add a search icon to the search bar
        search = QtGui.QIcon()
        search.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("snippets-playground/src/playground//search_icon.gif")))
        self.search_action = self.addAction(search, self.TrailingPosition)


        self.textChanged.connect(partial(self.transition_search_icon))

        # Add hidden text to the search bar
        self.setPlaceholderText("Search, do it!")
        
    def transition_search_icon(self, text):
        """Change the search icon to the clear icon if the text is not empty.
        
        Args:
            text (str): The text in the search bar.
        Returns:
            bool: True if the search icon was changed, False otherwise.
        """
        self.search_action = self.search_action or QtWidgets.QAction(self)
        
        if text:
            self.search_action.setVisible(False)
            self.setClearButtonEnabled(True)

        else:
            self.search_action.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("snippets-playground/src/playground/search_icon.gif"))))
            self.setClearButtonEnabled(False)
            self.search_action.setVisible(True)

        return True
    

class CollapsibleTreeView(QtWidgets.QTreeView):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)


        # Add buttons to the view

        item = QtWidgets.QAction("Item")

        
        self.addAction(item,)

        # Work on the header and add multiple buttons to the trailing position
        # self.header = self.header()
        # self.header.setSectionsClickable(True)
        # self.header.setSortIndicatorShown(True)
        # self.header.setStretchLastSection(True)
        # self.header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self.header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # self.header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        
        # # Add title to the header of the tree view
        # self.header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.header.customContextMenuRequested.connect(self.show_header_menu)


class ContextView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        self.view = CollapsibleTreeView()

        # Add a toolbar to the tree view
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addSeparator()
        self.toolbar.addAction("Item")
        self.toolbar.addAction("Item")
        self.toolbar.addAction("Item")
        # Add it to the tree view
        # self.view.addToolBar(self.toolbar)

        

        self.model = QtGui.QStandardItemModel()
        self.view.setModel(self.model)
        self.search_bar = SearchBarLineEdit()
        # Connect the text changed signal to the filter function
        self.search_bar.textChanged.connect(self.filter)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.search_bar)
        self.setLayout(self.layout)

        return
        # Add mulitple selection mode to the tree view
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # Expand the child if you click on the parent
        self.view.setExpandsOnDoubleClick(True)
        
        # Enable the windows always on top flag
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        
        # Always on the top
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # Add the flag

        # Have the window open in the center of the screen
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()

        # Get the center point of the screen
        center_point = screen_geometry.center()

        # Get the center point of the dialog
        dialog_rect = self.frameGeometry()
        dialog_rect.moveCenter(center_point)

        # Move the dialog to the center of the screen
        self.move(dialog_rect.topLeft())        
        
        # Create random items and add them to the trew view
        for i in range(5):
            # The items can not be editable
            parent = QtGui.QStandardItem(f"Parent {i}")
            parent.setEditable(False)
             # Remove the indicator from the parent items
            parent.setDropEnabled(False)
            
            for j in range(5):
                child = QtGui.QStandardItem(f"Child {j}")
                child.setEditable(False)
                parent.appendRow(child)
        
            self.model.appendRow(parent)
        
        # Move the children closer to fothe parent
        self.view.setIndentation(0)
        
        # Add folder icon to the parent items and file icon to the child items
        for parent in range(self.model.rowCount()):
            
            parent_item = self.model.item(parent)
            parent_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("snippets-playground/src/playground/sequence_icon.png")))
            parent_item.setIcon(parent_icon)
            
            # Remove the arrow from the parent items
            self.model.item(parent).setDropEnabled(False)
            
            # Remove the indicator from the parent items
            parent_item.setDropEnabled(False)
            
            # Rotate the icon when the item is expanded
            # self.view.expanded.connect(lambda index: self.rotate_icon(index))
            
            for child in range(self.model.item(parent).rowCount()):
                # Add arrow to the child items
                self.model.item(parent).child(child).setDropEnabled(False)
                # Make the icon smaller
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("snippets-playground/src/playground/shot_icon.png")))
                icon.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(":/arrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                # Set the size of the icon
                # Change the icon of the child items to be smaller
                
                self.model.item(parent).child(child).setIcon(icon)
                self.model.item(parent).child(child).setEditable(False)
        
        # Add a search bar at the bottom of the view to filter the items
        self.search_bar = SearchBarLineEdit()
        # Connect the text changed signal to the filter function
        self.search_bar.textChanged.connect(self.filter)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.search_bar)
        self.setLayout(self.layout)
    
    def filter(self, text: str) -> None:
        """Filter the items in the tree view based on the text in the search bar.
        """
        # Create a QSortFilterProxyModel
        proxy_model = QtCore.QSortFilterProxyModel()
        # Set its source model to the model of the tree view
        proxy_model.setSourceModel(self.model)
        # Set the filter regexp to the entered text
        proxy_model.setFilterRegExp(text)
        # Set the filter key column to the first column
        proxy_model.setFilterKeyColumn(0)
        # Set the proxy model as the model of the tree view
        self.view.setModel(proxy_model)
        # Have the filter work using regex instead of a fixed string
        self.view.setSortingEnabled(True)
        # Expand all items in the tree view if the results are true
        self.view.expandAll()
        
    def rotate_icon(self, index):
        """Rotate the icon of the expanded item.
        """
        item = self.model.itemFromIndex(index)
        icon = item.icon()
        transform = QtGui.QTransform()
        transform.rotate(90)
        rotated_icon = icon.pixmap(16, 16).transformed(transform)
        item.setIcon(QtGui.QIcon(rotated_icon))
        
    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """Close the application if the escape key is pressed.

        Args:
            event (QtGui.QKeyEvent): The key press event.

        Returns:
            bool: True if the event was handled, False otherwise.
        """
        super().keyPressEvent(event)
        # Close the application if the escape key is pressed
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            
            
            
            

if __name__ == "__main__":
    
    app = QtWidgets.QApplication([])
    context_view = ContextView()
    context_view.show()
    sys.exit(app.exec_())
    