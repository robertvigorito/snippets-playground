# pylint: disable=c-extension-no-member,too-few-public-methods
"""The module contains the tree view and the model for the tree view.
"""

import functools as _functools
import logging as _logging
import typing as _typing

# DCC import
import nuke as _nuke  # pylint: disable=import-error  # type: ignore
# PySide import
from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets

# Package import
from fpanel import pspecial as _pspecial
from fpanel.facade import Node as _Node

__all__ = ["NodeTreeView"]

_logger = _logging.getLogger(__name__)


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


class TreeviewPipeDelegate(_QtWidgets.QStyledItemDelegate):  # pylint: disable=too-few-public-methods
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
                bottom -= 5
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
        self._nodes: _typing.Dict[str, _Node] = {}
        model = _QtGui.QStandardItemModel()
        self.setModel(model)
        self.setAlternatingRowColors(True)
        # Set the headers to central alignment
        self.header().setDefaultAlignment(_QtCore.Qt.AlignmentFlag.AlignCenter)  # type: ignore[arg-type]
        self.setItemDelegateForColumn(0, TreeviewPipeDelegate(self))
        self.setItemDelegateForColumn(2, ComboBoxDelegate(self))
        # Define the toolbar and set the connections.
        self.toolbar = _pspecial.TreeToolbar()
        self.toolbar.expand.triggered.connect(self.expand_collapse)
        self.toolbar.refresh.triggered.connect(_functools.partial(self.populate, refresh=True))
        self.toolbar.goto.triggered.connect(self.goto)
        # Set the layout
        self.setLayout(self.toolbar)
        # Enable multi-selection
        self.setSelectionMode(_QtWidgets.QAbstractItemView.SelectionMode.ContiguousSelection)
        # Connect the signals and slots
        self.model().dataChanged.connect(self.update_node)
        # Create a right click menu for the tree view
        self.setContextMenuPolicy(_QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    @property
    def active_nodes(self) -> _typing.List[_Node]:
        """Return the active nodes in the tree view.

        Returns:
            list: A list of active nodes in the tree view.
        """
        return list(self._nodes.values())

    def leaveEvent(self, event: _QtCore.QEvent) -> None:  # pylint: disable=invalid-name
        """Override the leave event to hide the toolbar.

        Args:
            event (QEvent): The event object.
        """
        self.toolbar.toggle(on=False)

        return super().leaveEvent(event)

    def context_menu(self, point: _QtCore.QPoint) -> None:
        """Create a context menu for the tree view.

        Args:
            point (QPoint): The point where the context menu was requested.
        """
        menu = _QtWidgets.QMenu()
        # Create the actions
        goto_action = menu.addAction("Goto")
        show_properties_action = menu.addAction("Show Node on Properties")
        menu.addSeparator()
        disable_action = menu.addAction("Remove Node")
        # Add a separator
        menu.addSeparator()
        expand_collapse_action = menu.addAction("Expand/Collapse All")
        expand_collapse_selected_action = menu.addAction("Expand/Collapse Selected")
        # Connect the actions
        disable_action.triggered.connect(self.remove_item)
        expand_collapse_action.triggered.connect(self.expand_collapse)
        expand_collapse_selected_action.triggered.connect(_functools.partial(self.expand_collapse, selected=True))
        goto_action.triggered.connect(_functools.partial(self.goto, zoom=True))
        show_properties_action.triggered.connect(_functools.partial(self.goto, show=True))

        menu.exec_(self.viewport().mapToGlobal(point))

    def expand_collapse(self, selected: bool = False) -> bool:
        """Expand or collapse all the items in the tree view.

        Args:
            selected (bool, optional): Expand or collapse the selected items. Defaults to False.

        Returns:
            bool: True if the items were expanded or collapsed successfully, False otherwise.
        """
        if selected:
            for index in self.selectionModel().selectedRows():
                self.setExpanded(index, not self.isExpanded(index))
            return True

        if self.is_expanded():
            self.collapseAll()
        else:
            self.expandAll()
        return True

    def is_expanded(self) -> bool:
        """Return the expanded state of the tree view.

        Returns:
            bool: True if the tree view is expanded, False otherwise.
        """
        # Check if any of the items are expanded
        for index in range(self.model().rowCount()):
            if self.isExpanded(self.model().index(index, 0)):
                return True
        return False

    def enterEvent(self, event: _QtCore.QEvent) -> None:  # pylint: disable=invalid-name
        """Override the enter event to show the toolbar.

        Args:
            event (QEvent): The event object.
        """
        self.toolbar.toggle(on=True)
        return super().enterEvent(event)

    def goto(self, zoom=False, show=False) -> bool:
        """Go to the selected item in the tree view.

        Returns:
            bool: True if the item was selected successfully, False otherwise.
        """
        if not any([zoom, show]):
            return False

        if self.currentIndex().parent().isValid():
            index = self.currentIndex().parent()
        else:
            index = self.currentIndex()
        # Get the node from the index
        node = self._nodes.get(index.data() or "")
        if node and zoom:
            node.zoom()
        elif node and show:
            node.show()

        return True

    def remove_item(self) -> bool:
        """Disable the selected node in the tree view.

        Args:
            knob_name (str): The name of the knob to change.
            value (str): The value of the knob to change.

        Returns:
            bool: True if the node was changed successfully, False otherwise.
        """

        # Gather all selected items
        selected_items = []
        for index in self.selectedIndexes():
            if index.column() == 0:
                item = self.model().itemFromIndex(index)
                if item not in selected_items:
                    selected_items.append(item)

        # Remove items from bottom to top
        for item in sorted(selected_items, key=lambda x: x.row(), reverse=True):
            parent = item.parent() or self.model().invisibleRootItem()
            # Order matters, remove the node first
            self._nodes.pop(item.text(), None)
            # Remove the item from the model
            parent.removeRow(item.row())

        return True

    def mouseDoubleClickEvent(self, event: _QtGui.QMouseEvent) -> None:  # pylint: disable=invalid-name
        """Override the mouse press event to select the item under the cursor.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        current_index = self.indexAt(event.pos())
        item = self.model().itemFromIndex(current_index)
        # Get the first item in the row
        first_index = self.model().index(item.row(), 0, current_index.parent())
        first_item = self.model().itemFromIndex(first_index)

        if first_item.text() in self._nodes:
            self._nodes[first_item.text()].zoom()
            return
        super().mouseDoubleClickEvent(event)

    def update_node(self, model_index: _QtCore.QModelIndex) -> bool:
        """Update the node in the tree view.

        Returns:
            bool: True if the node was updated successfully, False otherwise.
        """
        # # Get the standard item from the model index
        item = self.model().itemFromIndex(model_index)
        node = self._nodes.get(item.parent().text()) or self._nodes.get(item.text())
        if not node:
            return False

        node.set(_Node.headers[model_index.column()], value=item.text())

        return True

    @show_wait_cursor
    def populate(self, nodes: _typing.Optional[list[_Node]] = None, refresh: bool = False) -> bool:
        """Populate the tree view with the given nodes.

        Args:
            nodes (list[str]): A list of nodes to populate the tree view.

        Returns:
            bool: True if the tree view was populated successfully, False otherwise.
        """
        if refresh:
            nodes = _Node.many()
        if not nodes:
            return False
        self._nodes = {node.full_name: node for node in nodes}
        self.model().clear()
        self.model().setHorizontalHeaderLabels([header.title() for header in _Node.headers])
        parent = self.model().invisibleRootItem()

        copied_nodes = self._nodes.copy()
        for node in copied_nodes.values():
            if not node.renderable():
                _logger.info("Skipping %s, it didn't pass the renderable check!", node.full_name)
                self._nodes.pop(node.full_name)
                continue
            item = _QtGui.QStandardItem(node.full_name)
            # Test adding a warning icon
            item.setIcon(_QtGui.QIcon(_pspecial.icon_path("warning")))
            # Make the icon animate in and out
            item.setToolTip(node.full_name)
            item.setEditable(False)
            appendable_items: _typing.List[_QtGui.QStandardItem] = []
            for node_item_value in node:
                node_column_data = _QtGui.QStandardItem(str(node_item_value))
                node_column_data.setEditable(node_item_value != node.basename)
                appendable_items.append(node_column_data)

            parent.appendRow(item)
            item.appendRow(appendable_items)

        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
            if column == 1:
                self.setColumnWidth(column, self.columnWidth(column) + 20)
        return True


class ComboBoxDelegate(_QtWidgets.QStyledItemDelegate):
    """A custom delegate for the combo box in the tree view"""

    def __init__(self, parent=None) -> None:  # pylint: disable=useless-parent-delegation
        """Initialize the combo box delegate.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__(parent)

    def createEditor(self, parent, option, index) -> _QtWidgets.QComboBox:  # pylint: disable=invalid-name
        """Create the editor for the combo box delegate.

        Args:
            parent (QWidget): The parent widget.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            QComboBox: The combo box editor.
        """

        editor = _QtWidgets.QComboBox(parent)

        editor.addItems(["all", "none"] + _nuke.layers())
        super().createEditor(parent, option, index)
        return editor


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    tree = NodeTreeView()
    tree.show()
    sys.exit(app.exec_())
