from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt

class MappingCanvas(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        item_text = event.mimeData().text()

        # Add mapping row
        self.addItem(f"Mapped → {item_text}")
        event.accept()