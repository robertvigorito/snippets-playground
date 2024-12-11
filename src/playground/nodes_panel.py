from PySide2 import QtWidgets as _QtWidgets, QtCore as _QtCore, QtGui as _QtGui



class ChipsComponent(QtWidgets.QWidget):
    """
    A sub-widget used internally in the ChipsWidget to render the chips, keep track of the chips
    and handle ui interaction.
    """

    chipAdded = _QtCore.Signal(str)
    chipRemoved = _QtCore.Signal(str)
    chipsChanged = _QtCore.Signal(list)

    def __init__(self):
        super(ChipsComponent, self).__init__()

        self.chips = []
        self.minHeight = 1
        self.setMinimumHeight(self.minHeight)

        # Define the colors used in the widget
        self.chipBGColor = _QtGui.QColor(150, 150, 150)
        self.chipBorderColor = _QtGui.QColor(255, 255, 255)
        self.chipTextColor = _QtGui.QColor(0, 0, 0)

        self.draggingTextColor = _QtGui.QColor(255, 255, 255, 150)
        self.draggingBGColor = _QtGui.QColor(150, 150, 150, 100)
        self.draggingBorderColor = _QtGui.QColor(25, 25, 25, 50)

        self.placeHolderBorderColor = _QtGui.QColor(255, 255, 255, 50)
        self.placeHolderBGColor = _QtGui.QColor(150, 150, 150, 50)

        self.font = _QtGui.QFont("San-Serif", 10, _QtGui.QFont.Normal)

        # Define other UI parameters
        self.radius = 7
        self.padding = [5, 5]
        self.chipHeight = 20

        # Initialize parameters used to track/render the dragged chips
        self.selectedChip = None
        self.dragStart = [-1, -1]
        self.dragEnd = [-1, -1]
        self.dragging = False
        self.dragOffset = [0, 0]

    def paintEvent(self, e):
        qp = _QtGui.QPainter(self)
        self.drawWidget(qp, e)
        self.setFixedHeight(self.minHeight)
        super(ChipsComponent, self).paintEvent(e)

    def mousePressEvent(self, e):
        """
        Process mouse button press.
        """
        x = e.x()
        y = e.y()

        # Reset dragging parameters
        self.selectedChip = None
        self.dragStart = [-1, -1]
        self.draggedChipIndex = -1
        self.dragging = False

        for i, chip in enumerate(self.chips):

            # Check if the click is inside a chip
            bbLeft, bbRight, bbTop, bbBottom = chip["bbox"]
            if x >= bbLeft and x <= bbRight and y >= bbTop and y <= bbBottom:

                # Check if the click is on the closing "x" of the chip
                left, right, top, bottom = chip["closeBox"]
                if x >= left and x <= right and y >= top and y <= bottom:
                    self.chips.remove(chip)
                    self.chipRemoved.emit(chip["text"])
                    self.chipsChanged.emit([chip["text"] for chip in self.chips])
                    break

                # If the chip wasn't closed, set up the dragging information
                self.draggedChipIndex = i
                self.selectedChip = chip
                self.dragStart = [x, y]
                self.dragEnd = [x, y]
                self.dragging = True
                self.dragOffset = [x - bbLeft, y - bbTop]

        self.update()

    def getChipCenter(self, chip):
        """
        Get the center point of the given chip.
        """
        left, right, top, bottom = chip["bbox"]
        return ((left + right) / 2.0, (top + bottom) / 2.0)

    def isInChip(self, position, chip):
        """
        Check if the given position falls within the borders of the given chip.
        """
        left, right, top, bottom = chip["bbox"]
        x, y = position
        return x >= left and x <= right and y >= top and y <= bottom

    def mouseMoveEvent(self, e):
        """
        Process a mouse move event.
        """
        # If nothing is being dragged, there's nothing to do
        if not self.selectedChip:
            return

        self.dragEnd = [e.x(), e.y()]

        # Figure out if we need to reorder
        if self.dragging:
            center = list(self.getChipCenter(self.selectedChip))
            center[0] += self.dragEnd[0] - self.dragStart[0]
            center[1] += self.dragEnd[1] - self.dragStart[1]

            for i, chip in enumerate(self.chips):
                if chip == self.selectedChip:
                    continue

                # If a chip was dragged into another chip
                if self.isInChip(center, chip):

                    insertInto = i

                    # Compare positions to figure out if we should insert before or after the
                    # current chip
                    if center[0] > self.getChipCenter(chip)[0]:
                        insertInto += 1
                    insertInto = max(0, min(insertInto, len(self.chips) - 1))

                    # Moving to the left
                    if insertInto != self.draggedChipIndex:
                        # Update the order in the list
                        new_order = copy.deepcopy(self.chips)
                        c = new_order.pop(self.draggedChipIndex)
                        new_order.insert(insertInto, c)

                        # Update the information required for the dragging to render correctly
                        self.draggedChipIndex = insertInto
                        self.selectedChip = new_order[insertInto]
                        self.updateValues(new_order)
                        left, right, top, bottom = self.selectedChip["bbox"]
                        self.dragStart[0] = left + self.dragOffset[0]
                        self.dragStart[1] = top + self.dragOffset[1]

                        self.chips = new_order

        self.update()

    def mouseReleaseEvent(self, e):
        """
        Process a mouse release event.
        """
        self.dragStart = [-1, -1]
        self.dragEnd = [-1, -1]
        self.dragging = False
        if self.selectedChip:
            self.selectedChip = None
            self.chipsChanged.emit([chip["text"] for chip in self.chips])
        self.update()

    def addChip(self, chipText):
        """
        Add a chip.
        """
        self.chips.append({"text": chipText, "closeBox": []})
        self.chipAdded.emit(chipText)
        self.chipsChanged.emit([chip["text"] for chip in self.chips])
        self.setFixedHeight(self.minHeight)
        self.update()

    def getChips(self):
        """
        Get an ordered list of all the chips.
        """
        return [str(chip["text"]) for chip in self.chips]

    def removeChip(self, chipText):
        """
        Remove a chip with given text.

        :param str chipText:
            Chip with given text to remove.
        """
        for chip in self.chips[:]:
            if chip["text"] == chipText:
                self.chips.remove(chip)
                self.chipRemoved.emit(chip["text"])

    def clear(self):
        """
        Clear all chips.
        """
        for chip in self.chips[:]:
            self.chips.remove(chip)
            self.chipRemoved.emit(chip["text"])

    def drawWidget(self, qp, e=None):
        """
        Draw the widget.
        """
        self.updateValues(self.chips)

        fm = _QtGui.QFontMetrics(self.font)

        # Draw static chips
        for chip in self.chips:

            left, right, top, bottom = chip["bbox"]

            # Draw the chip's background rectangle
            # (different style for regular chips and dragging chips)
            if not self.selectedChip == chip or not self.dragging:
                qp.setBrush(self.chipBGColor)
                qp.setPen(self.chipBorderColor)
            else:
                qp.setBrush(self.placeHolderBGColor)
                qp.setPen(self.placeHolderBorderColor)
            qp.drawRoundedRect(left, top, right - left, bottom - top, self.radius, self.radius)

            # Draw the text
            if not self.selectedChip == chip or not self.dragging:
                qp.setPen(self.chipTextColor)
                qp.drawText(
                    left + self.radius, top + fm.height() / 2.0 + self.radius, chip["renderText"]
                )

        # Draw the dragging chip
        if self.selectedChip and self.dragging:
            # Find the source chips position
            left, right, top, bottom = self.selectedChip["bbox"]

            # Find the current offset
            xOffset = self.dragEnd[0] - self.dragStart[0]
            yOffset = self.dragEnd[1] - self.dragStart[1]

            x = self.dragEnd[0] - self.dragOffset[0]
            y = self.dragEnd[1] - self.dragOffset[1]

            # Draw the box
            qp.setPen(self.draggingBorderColor)
            qp.setBrush(self.draggingBGColor)
            qp.drawRoundedRect(x, y, right - left, bottom - top, self.radius, self.radius)

            # Draw the text
            qp.setPen(self.draggingTextColor)
            qp.drawText(
                x + self.radius, y + fm.height() / 2.0 + self.radius, self.selectedChip["text"]
            )

            # Resize the widget if necessary
        if self.chips:
            self.minHeight = self.chips[-1]["bbox"][2] + self.chipHeight + 5
        else:
            self.minHeight = 1

    def updateValues(self, chips):
        """
        Update the position parameters on the chips. Used for rendering the chips.
        """
        size = self.size()
        w = size.width()
        h = size.height()

        fm = _QtGui.QFontMetrics(self.font)

        xPos = self.padding[0]
        yPos = self.padding[1]

        for i, chip in enumerate(chips):

            chip["renderText"] = chip["text"] + "   x"
            chip["width"] = fm.width(chip["renderText"]) + 2 * self.radius

            # Go to the next line if necessary
            if chip["width"] + self.padding[0] + xPos > w and xPos > self.padding[0]:
                xPos = self.padding[0]
                yPos += self.chipHeight + self.padding[1]

            # Store the location of the chip
            chip["bbox"] = [xPos, xPos + chip["width"], yPos, yPos + self.chipHeight]

            # Register the area that will close this chip
            left = xPos + fm.width(chip["text"] + " ") + self.radius
            right = left + fm.width(" x ")
            top = yPos
            bottom = top + fm.height()
            chip["closeBox"] = [left, right, top, bottom]

            # Advance the x position
            xPos += fm.width(chip["renderText"]) + 2 * self.radius + self.padding[0]



class VersionDropdown(_QtWidgets.QComboBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setEditable(True)

        # Draw a label out of a rectangle and add it as an item

        self.addItems(["", "auto", "script"])

        # Tooltip
        self.setToolTip(
            """
The auto option will use the latest version.
If you want to use a version that the script is using, select script.

Else, manually add the version number.
"""
        )

        # Text change event
        self.lineEdit().textChanged.connect(self.on_text_changed)
        self.lineEdit().setLayout(_QtWidgets.QHBoxLayout())

        label_frame = _QtWidgets.QFrame()
        label_frame.setStyleSheet("border:1px solid rgb(192, 192, 192); border-radius: 4px;")
        label_frame.setContentsMargins(0, 0, 0, 0)
        label_frame.setFixedHeight(28)
        label_frame.setFixedWidth(100)

        # label_frame.setFrameStyle(_QtWidgets.QFrame.Panel | _QtWidgets.QFrame.Raised)
        # label_frame.setLineWidth(1)
        # label_frame.setMidLineWidth(1)

        # Add the label to the layout
        label_frame.setLayout(_QtWidgets.QHBoxLayout())

        label_frame.layout().addWidget(_QtWidgets.QLabel("Testing"))

        self.lineEdit().layout().addWidget(label_frame)
        self.lineEdit().layout().setContentsMargins(0, 0, 0, 0)
        # Set right alignment
        self.lineEdit().setAlignment(_QtCore.Qt.AlignLeft)

    def on_text_changed(self, text: str) -> None:
        # The text can only be a number or values in the list
        if text not in ["", "auto", "script"] and not text.isdigit():
            self.setCurrentText("")

        return

    def changeEvent(self, e: _QtCore.QEvent) -> None:
        print(e)
        return super().changeEvent(e)


class NodePanel(_QtWidgets.QDialog):
    CATERGORY = ("comp", "light", "enviro", "fx")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        form_layout = _QtWidgets.QFormLayout()
        self.setLayout(form_layout)

        form_layout.addRow("level", _QtWidgets.QLineEdit())

        category_combobox = _QtWidgets.QComboBox()
        form_layout.addRow("category", category_combobox)
        # Description
        form_layout.addRow("description", _QtWidgets.QLineEdit())
        # Version


        self.chips = ChipsComponent()
        form_layout.addRow("version", VersionDropdown())

        # Label form to the right
        form_layout.setLabelAlignment(_QtCore.Qt.AlignRight)

        # Add a button that will have multiple actions
        button = _QtWidgets.QPushButton("Create")
        menu = _QtWidgets.QMenu(button)
        menu.addAction("Create")
        menu.addAction("Update")
        menu.addAction("Delete")
        button.setMenu(menu)
        form_layout.addWidget(button)

        # Set in the middle of the screen
        self.setGeometry(0, 0, 300, 200)
        screen = _QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        window_size = self.size()
        x = (screen_size.width() - window_size.width()) / 2
        y = (screen_size.height() - window_size.height()) / 2 - 300
        self.move(x, y)

        # Add shortcuts to close the window
        close_shortcut = _QtWidgets.QShortcut(_QtGui.QKeySequence("alt+w"), self)
        close_shortcut.activated.connect(self.close)

    def pathing(self):
        """Build the path from the parameters in the panel"""
        # shared/img/snapshot_type/level_description_version.extension/level_description_version.padding.exr
        pass


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    window = NodePanel()
    window.show()
    sys.exit(app.exec_())
