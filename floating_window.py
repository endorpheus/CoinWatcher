import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPainter, QColor
from PyQt6.QtCore import Qt, QPoint

class FloatingPriceWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.background_color = QColor(75, 0, 130, 204)  # Default color
        self.text_color = QColor(255, 255, 255)  # Default text color (white)

        layout = QVBoxLayout()
        self.price_label = QLabel()
        self.price_label.setStyleSheet(f"color: {self.text_color.name()}; font-size: 16px;")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)

        self.setLayout(layout)

        self.dragging = False
        self.offset = QPoint()

        # Set the window icon, TODO add fallback image if not found
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'coin.png')))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.background_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.position().toPoint()) - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def update_price(self, price_text):
        self.price_label.setText(price_text)

    def set_background_color(self, color, opacity=0.8):
        self.background_color = QColor(color)
        self.background_color.setAlphaF(opacity)
        self.update()

    def set_text_color(self, color):
        self.text_color = QColor(color)
        self.price_label.setStyleSheet(f"color: {self.text_color.name()}; font-size: 16px;")
