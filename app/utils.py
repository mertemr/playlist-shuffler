from PyQt6.QtGui import QStandardItem, QFont, QColor
from app.globals import DEFAULT_FONT


class StandardItem(QStandardItem):
    def __init__(
        self,
        text="",
        bold=False,
        color=(255,255,255),
        size=9,
    ):
        super().__init__()
        
        font = QFont(DEFAULT_FONT, size)
        font.setBold(bold)
        
        self.setEditable(False)
        self.setForeground(QColor(*color))
        self.setFont(font)
        self.setText(text)
