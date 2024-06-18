from typing import Optional
from PySide2 import QtWidgets, QtGui, QtCore


class TreeviewPipeDelegate(QtWidgets.QStyledItemDelegate):
    """A custom delegate for the tree view that draws a pipe between the parent and child items."""

    def __init__(self, parent: "QtWidgets.QTreeView"):
        super().__init__(parent)
        self.parent_view = parent
        self.orange_pen = QtGui.QPen(QtGui.QColor(210, 122, 17), 2, QtCore.Qt.SolidLine)
        self.light_orange_pen = QtGui.QPen(QtGui.QColor(210, 122, 17, 150), 2, QtCore.Qt.SolidLine)
        self.light_blue_pen = QtGui.QPen(QtGui.QColor(0, 0, 255, 50), 2, QtCore.Qt.SolidLine)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        """Override the paint method to draw a pipe between the parent and child items.

        Args:
            painter (QPainter): The painter object used to draw the item.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            bool: True if the item was painted. Otherwise, False.
        """
        super().paint(painter, option, index)
        has_children = self.parent_view.model().hasChildren(index)
        not_last = index.model().index(index.row() + 1, index.column(), index.parent()).isValid()

        painter.setPen(self.orange_pen)

        left, top, right, bottom = (  # pylint: disable=unused-variable
            option.rect.left(),
            option.rect.top(),
            option.rect.right(),
            option.rect.bottom(),
        )
        offset_left = left - 10

        if index.parent().isValid() and not has_children and not_last:
            painter.drawLine(offset_left, top, offset_left, bottom)

        # Draw the horizontal line at the end of the children with no children
        elif index.parent().isValid() and not not_last and not has_children:
            painter.drawLine(left - 10, top, left - 10, bottom - 10)
            painter.drawLine(left - 10, bottom - 10, left, bottom - 10)

        if has_children and not_last:
            next_item_rect = option.widget.visualRect(model.index(index.row() + 1, index.column(), index.parent()))
            painter.setPen(self.light_orange_pen)
            painter.drawLine(left - 10, bottom, left - 10, next_item_rect.top())

        return True


#
# Create the application and the model
app = QtWidgets.QApplication([])

# Create the tree view
tree = QtWidgets.QTreeView()
model = QtGui.QStandardItemModel()

# Set the header labels
model.setHorizontalHeaderLabels(["Tree", "Names"])

# Create the root item
for i in range(2):
    parent_item = QtGui.QStandardItem(f"Parent {i}")
    model.appendRow(parent_item)
    for j in range(3):
        child_item = QtGui.QStandardItem(f"Child {j}")
        parent_item.appendRow(child_item)

    for rand in range(2):
        child_item = QtGui.QStandardItem(f"Child {i}{rand}")
        parent_item.appendRow(child_item)

for i in range(2):
    parent_item = QtGui.QStandardItem(f"No Child 2 {i}")
    model.appendRow(parent_item)

tree.setModel(model)
# Set the custom delegate for the tree view
delegate = TreeviewPipeDelegate(tree)
tree.setItemDelegate(delegate)

# Resize the columns to fit the content
tree.resizeColumnToContents(0)
tree.expandAll()
tree.resize(800, 600)
# Show the tree view
tree.show()
app.exec_()
