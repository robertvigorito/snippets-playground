import sys
from PySide6 import QtCore, QtGui, QtWidgets

class TreeViewExample(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TreeView Example")
        self.setGeometry(100, 100, 400, 300)

        self.setup_tree_view()
        self.create_button()

    def setup_tree_view(self):
        self.tree_view = QtWidgets.QTreeView(self)
        self.tree_view.setGeometry(QtCore.QRect(10, 40, 380, 240))

        # Create a QStandardItemModel to hold the data for the tree view
        model = QtGui.QStandardItemModel()
        self.tree_view.setModel(model)

        # Add some items to the model
        root_item = model.invisibleRootItem()
        self.add_items(root_item, "Root Item", ["Item 1", "Item 2", "Item 3"])

    def add_items(self, parent_item, text, children):
        parent_item.appendRow(QtGui.QStandardItem(text))
        for child_text in children:
            parent_item.appendRow(QtGui.QStandardItem(child_text))

    def create_button(self):
        self.button = QtWidgets.QPushButton("Toggle Collapse", self)
        self.button.setGeometry(QtCore.QRect(10, 10, 150, 25))
        self.button.clicked.connect(self.toggle_collapse)

    def toggle_collapse(self):
        root_index = self.tree_view.rootIndex()
        is_expanded = not self.tree_view.isExpanded(root_index)
        self.tree_view.setExpanded(root_index, is_expanded)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TreeViewExample()
    window.show()
    sys.exit(app.exec_())
