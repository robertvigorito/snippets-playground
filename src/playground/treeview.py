"""Play around with creating a widget that displays a tree of items.
"""
import sys
from PySide2 import QtCore, QtWidgets, QtGui


class SearchBarLineEditold(QtWidgets.QLineEdit):
    
    def __init__(self) -> None:
        super().__init__()
        
        # Add a search icon to the search bar
        search = QtGui.QIcon()
        search.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("/home/rvigorito/dev/playground/src/playground/search_icon.gif")))
        search_action = self.addAction(search, QtWidgets.QLineEdit.LeadingPosition)
        
        # Turn off the search action when the text is added with a smooth transition
        # Transition the search icon to a close icon
        
        self.textChanged.connect(lambda text: search_action.setVisible(not bool(text)))
        self.setClearButtonEnabled(True)
        
        # Add a close icon to the search bar
        close = QtGui.QIcon()
        close.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("/home/rvigorito/dev/playground/src/playground/close_icon.png")))
        # close_action = self.addAction(close, QtWidgets.QLineEdit.TrailingPosition)

        # Clear text if the mouse is clicked on the icon
            
class SearchBarLineEdit(QtWidgets.QLineEdit):
    
    def __init__(self) -> None:
        super().__init__()
        
        # Add a search icon to the search bar
        search = QtGui.QIcon()
        search.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("/home/rvigorito/dev/playground/src/playground/search_icon.gif")))
        search_action = self.addAction(search, self.TrailingPosition)
        
        # Turn off the search action when the text is added with a smooth transition
        # Transition the search icon to a close icon
        self.animation = QtCore.QPropertyAnimation(search_action, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: search_action.setVisible(False))
        self.textChanged.connect(lambda text: self.animate_search_icon(search_action, bool(text)))
        
        
        # enable the clear button when the animation finishes
        self.animation.finished.connect(lambda: self.setClearButtonEnabled(not bool(self.text())))
        
        # Add a close icon to the search bar
        close = QtGui.QIcon()
        close.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("/home/rvigorito/dev/playground/src/playground/close_icon.png")))
        # close_action = self.addAction(close, QtWidgets.QLineEdit.TrailingPosition)

        # Clear text if the mouse is clicked on the icon
        
    def 
        
    def animate_search_icon(self, search_action, visible):
        if visible:
            search_action.setVisible(True)
            self.animation.setDirection(QtCore.QAbstractAnimation.Forward)
            self.animation.start()
        else:
            self.animation.setDirection(QtCore.QAbstractAnimation.Backward)
            self.animation.start()



class ContextView(QtWidgets.QDialog):
    def __init__(self) -> None:
        super().__init__()
        
        self.view = QtWidgets.QTreeView()
        self.model = QtGui.QStandardItemModel()
        self.view.setModel(self.model)
        # Add mulitple selection mode to the tree view
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # Expand the child if you click on the parent
        self.view.setExpandsOnDoubleClick(True)
        
        # Enable the windows always on top flag
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        
        # Always on the top
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        
        
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
            parent_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("playground/src/playground/sequence_icon.png")))
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
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("playground/src/playground/shot_icon.png")))
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
    