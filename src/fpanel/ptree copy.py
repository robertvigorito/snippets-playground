import random
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

        painter.save()

        has_children = self.parent_view.model().hasChildren(index)
        not_last = index.model().index(index.row() + 1, index.column(), index.parent()).isValid()

        painter.setPen(self.orange_pen)

        left, top, right, bottom = (  # pylint: disable=unused-variable
            option.rect.left(),
            option.rect.top(),
            option.rect.right(),
            option.rect.bottom(),
        )
        option.rect = QtCore.QRect(left, top, right - left, bottom - top)
        offset_left = left - 10

        if index.parent().isValid() and not has_children:
            if not not_last:
                bottom -= 10
                painter.drawLine(offset_left, bottom, offset_left + 10, bottom)
            painter.drawLine(offset_left, top, offset_left, bottom)

        if has_children and index.parent().isValid() and self.parent_view.isExpanded(index):

            # Get the last child item of all the children
            original_index = index

            while index.model().hasChildren(index):
                index = index.child(index.model().rowCount(index) - 1, 0)

            last_child_rect = self.parent_view.visualRect(index)
            painter.setPen(self.light_orange_pen)

            if self.parent_view.isExpanded(index.parent()):
                painter.drawLine(offset_left, bottom, offset_left, last_child_rect.bottom() - 5)

            # Are all the children expanded?
            children_list = [original_index.child(i, 0) for i in range(original_index.model().rowCount(original_index))]

            if children_list and not self.parent_view.isExpanded(children_list[-1]):
                last_child_rect = self.parent_view.visualRect(children_list[-1])
                painter.setPen(self.light_blue_pen)
                painter.drawLine(offset_left, bottom, offset_left, last_child_rect.bottom())

        painter.restore()

        return True


class TreeviewPipe(QtWidgets.QTreeView):

    def __init__(self) -> None:
        super().__init__()

        # self.setIndentation(20)
        # self.setRootIsDecorated(False)
        self.resize(800, 600)
        # self.setAllColumnsShowFocus(True)

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "Class", "Basename", "Order", "Frange"])

        self.setModel(model)

        QtWidgets.QShortcut("alt+w", self, self.close)

        for i in range(2):
            parent = QtGui.QStandardItem(f"Parent {i}")

            for j in range(random.randint(1, 3)):
                child = QtGui.QStandardItem(f"Child {j}")
                parent.appendRow(child)
                for k in range(random.randint(2, 4)):
                    new_child = QtGui.QStandardItem(f"Child {j}.{k}")
                    child.appendRow(new_child)
                    new_child.appendRows([QtGui.QStandardItem(f"{k} column") for k in range(random.randint(2, 7))])

            model.appendRow(parent)
        # Assign the delegate to the tree view
        self.setItemDelegate(TreeviewPipeDelegate(self))

        self.expandAll()
        self.move(3500, 100)

        for column in range(model.columnCount()):
            self.resizeColumnToContents(column)
            # Add some padding to the column width
            self.setColumnWidth(column, self.columnWidth(column) + 50)

        # Increase the font size
        font = self.font()
        font.setPointSize(11)
        # self.setFont(font)
        # self.setAlternatingRowColors(True)


app = QtWidgets.QApplication([])

TreeView = TreeviewPipe()
TreeView.show()

app.exec_()
