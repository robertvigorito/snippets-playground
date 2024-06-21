"""The module contains the tree view and the model for the tree view.
"""

import functools as _functools
import typing as _typing

from PySide2 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore


# Package import
from fpanel import pspecial as _pspecial
from fpanel.facade import Node as _Node


__all__ = ["NodeTreeView"]


def show_wait_cursor(func: _typing.Callable) -> _typing.Callable:
    """A decorator that shows the wait cursor during the execution of the function.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """

    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            _QtWidgets.QApplication.setOverrideCursor(_QtGui.QCursor(_QtCore.Qt.CursorShape.WaitCursor))
            result = func(*args, **kwargs)
        finally:
            _QtWidgets.QApplication.restoreOverrideCursor()
        
        return result

    return wrapper


class TreeviewPipeDelegate(_QtWidgets.QStyledItemDelegate):
    """A custom delegate for the tree view that draws a pipe between the parent and child items."""

    def __init__(self, parent: "_QtWidgets.QTreeView") -> None:
        """Initialize the delegate.

        Args:
            parent (QtWidgets.QTreeView): The parent tree view.
        """
        super().__init__(parent)
        self.parent_view = parent
        self.model = parent.model()
        self.orange_pen = _QtGui.QPen(_QtGui.QColor(210, 122, 17), 2, _QtCore.Qt.SolidLine)
        self.light_orange_pen = _QtGui.QPen(_QtGui.QColor(210, 122, 17, 150), 2, _QtCore.Qt.SolidLine)
        self.light_blue_pen = _QtGui.QPen(_QtGui.QColor(0, 0, 255, 50), 2, _QtCore.Qt.SolidLine)

    def paint(self, painter: _QtGui.QPainter, option: _QtWidgets.QStyleOptionViewItem, index: _QtCore.QModelIndex):
        """Override the paint method to draw a pipe between the parent and child items.

        Args:
            painter (QPainter): The painter object used to draw the item.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            bool: True if the item was painted. Otherwise, False.
        """
        super().paint(painter, option, index)

        # Save the painter state
        painter.save()
        # Check if the item has children and if it's not the last item
        has_children = self.parent_view.model().hasChildren(index)
        not_last = index.model().index(index.row() + 1, index.column(), index.parent()).isValid()
        # Set the pen color based on the item's depth, default to orange
        painter.setPen(self.orange_pen)
        # Easy mapping of the rect values
        left, top, _, bottom = (option.rect.left(), option.rect.top(), option.rect.right(), option.rect.bottom())
        offset_left = left - 10

        # Draw the pipe between the items that dont have children
        if index.parent().isValid() and not has_children:
            if not not_last:
                bottom -= 10
                painter.drawLine(offset_left, bottom, offset_left + 10, bottom)
            painter.drawLine(offset_left, top, offset_left, bottom)

        # Draw the pipe between the parent and the children but ignore the top parent
        if has_children and index.parent().isValid() and self.parent_view.isExpanded(index):
            # Get the last child item of all the children
            last_child_index = index
            while self.model.hasChildren(last_child_index):
                last_child_index = last_child_index.child(self.model.rowCount(last_child_index) - 1, 0)
            last_child_rect = self.parent_view.visualRect(last_child_index)
            # Set the pen color to light orange for contrast
            painter.setPen(self.light_orange_pen)

            if self.parent_view.isExpanded(index.parent()):
                painter.drawLine(offset_left, bottom, offset_left, last_child_rect.bottom() - 5)

            # Fixes if the last child is not visible, blue for levels.
            children_list = [index.child(i, 0) for i in range(index.model().rowCount(index))]
            if children_list and not self.parent_view.isExpanded(children_list[-1]):
                last_child_rect = self.parent_view.visualRect(children_list[-1])
                painter.setPen(self.light_blue_pen)
                painter.drawLine(offset_left, bottom, offset_left, last_child_rect.bottom())

        painter.restore()

        return True


class NodeTreeView(_QtWidgets.QTreeView):
    """A custom tree view for displaying Nuke nodes and interacting with them."""

    def __init__(self, parent: _typing.Optional["_QtWidgets.QWidget"] = None) -> None:
        """Initialize the tree view with the given parent widget.

        Args:
            parent (QWidget, optional): The parent widget of the tree view. Defaults
        """
        super().__init__(parent)
        self._nodes: list[_Node] = []
        model = _QtGui.QStandardItemModel()
        self.setModel(model)
        self.setAlternatingRowColors(True)
        # Set the headers to central alignment
        self.header().setDefaultAlignment(_QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setItemDelegateForColumn(0, TreeviewPipeDelegate(self))
        # Define the toolbar and set the connections.
        self.toolbar = _pspecial.TreeToolbar()
        self.toolbar.expand.triggered.connect(self.expand_collapse)
        self.toolbar.refresh.triggered.connect(_functools.partial(self.populate, refresh=True))
        self.toolbar.goto.triggered.connect(self.goto)
        # Set the layout
        self.setLayout(self.toolbar)
        # Set the expanded state
        self.expanded = False

        # Connect the signals and slots
        self.model().dataChanged.connect(self.update_node)

    def expand_collapse(self):
        """Expand or collapse all the items in the tree view."""
        if self.expanded:
            self.collapseAll()
            self.expanded = False
        else:
            self.expandAll()
        return True

    def expandAll(self) -> None:  # pylint: disable=invalid-name
        """Expand all the items in the tree view."""
        self.expanded = True
        return super().expandAll()

    def enterEvent(self, event: _QtCore.QEvent) -> None:  # pylint: disable=invalid-name
        """Override the enter event to show the toolbar.

        Args:
            event (QEvent): The event object.
        """
        self.toolbar.toggle(on=True)
        return super().enterEvent(event)
    
    def goto(self):
        """Go to the selected item in the tree view."""

        # Get the parent index if the item is a child
        if self.currentIndex().parent().isValid():
            index = self.currentIndex().parent().row()
        else:
            index = self.currentIndex().row()
        self._nodes[index].zoom()

        return True

    def leaveEvent(self, event: _QtCore.QEvent) -> None:  # pylint: disable=invalid-name
        """Override the leave event to hide the toolbar.

        Args:
            event (QEvent): The event object.
        """
        self.toolbar.toggle(on=False)

        return super().leaveEvent(event)

    def update_node(self, model_index: _QtCore.QModelIndex) -> bool:
        """Update the node in the tree view.

        Returns:
            bool: True if the node was updated successfully, False otherwise.
        """
        # Get the standard item from the model index
        item = self.model().itemFromIndex(model_index)
        item.node.set(_Node.headers[model_index.column()], value=item.text())

        return True


    @show_wait_cursor
    def populate(self, nodes: _typing.Optional[list[_Node]] = None, refresh: bool = False) -> bool:
        """Populate the tree view with the given nodes.

        Args:
            nodes (list[str]): A list of nodes to populate the tree view.

        Returns:
            bool: True if the tree view was populated successfully, False otherwise.
        """

        self._nodes = nodes or self._nodes
        if not self._nodes:
            return False
        self.model().clear()
        self.model().setHorizontalHeaderLabels([header.title() for header in _Node.headers])

        parent = self.model().invisibleRootItem()
        for node in self._nodes:
            if refresh:
                node.define()
            item = _QtGui.QStandardItem(node.full_name)
            item.setEditable(False)
            appendable_items: _typing.List[_QtGui.QStandardItem] = []
            for node_item_value in node:
                node_column_data = _QtGui.QStandardItem(str(node_item_value))
                node_column_data.setEditable(node_item_value != node.basename)
                node_column_data.node = node
                appendable_items.append(node_column_data)
            parent.appendRow(item)
            item.appendRow(appendable_items)

        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
            if column == 1:
                self.setColumnWidth(column, self.columnWidth(column) + 20)

        return True
