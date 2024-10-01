import sys
import os
import json
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QMenu, QSystemTrayIcon, QSizePolicy, QPushButton, QListWidget
from PyQt6.QtGui import QIcon, QAction, QPixmap, QCursor, QScreen, QColor, QPainter, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QPoint

class CryptoTicker(QWidget):
    def __init__(self):
        super().__init__()
        self.ticker = "bitcoin"
        self.interval = 300
        self.current_price = None
        self.previous_price = None
        self.high_threshold = None
        self.low_threshold = None
        self.favorite_tickers = self.load_favorite_tickers()
        self.initUI()

        # Make the window borderless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Variables for dragging
        self.dragging = False
        self.offset = QPoint()

    def initUI(self):
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'coin.png')
        self.custom_icon = QIcon(self.icon_path)

        layout = QVBoxLayout()

        # Ticker input and favorites
        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        self.ticker_input = QLineEdit(self.ticker)
        self.ticker_input.editingFinished.connect(self.update_ticker)
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_input)
        layout.addLayout(ticker_layout)

        # Favorites list
        self.favorites_list = QListWidget()
        self.favorites_list.addItems(self.favorite_tickers)
        self.favorites_list.itemClicked.connect(self.select_favorite)
        layout.addWidget(self.favorites_list)

        # Add/Remove favorite buttons
        fav_buttons_layout = QHBoxLayout()
        add_fav_button = QPushButton("Add Favorite")
        add_fav_button.clicked.connect(self.add_favorite)
        remove_fav_button = QPushButton("Remove Favorite")
        remove_fav_button.clicked.connect(self.remove_favorite)
        fav_buttons_layout.addWidget(add_fav_button)
        fav_buttons_layout.addWidget(remove_fav_button)
        layout.addLayout(fav_buttons_layout)

        # Interval slider
        interval_layout = QVBoxLayout()
        interval_label = QLabel("Interval (seconds):")
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(30)
        self.interval_slider.setMaximum(1500)
        self.interval_slider.setValue(self.interval)
        self.interval_slider.setTickInterval(100)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.valueChanged.connect(self.update_interval)

        self.slider_value_label = QLabel(f"Current interval: {self.interval} seconds")

        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.slider_value_label)
        layout.addLayout(interval_layout)

        # Thresholds
        threshold_layout = QHBoxLayout()
        low_label = QLabel("Low Threshold:")
        self.low_threshold_input = QLineEdit()
        self.low_threshold_input.setPlaceholderText("Enter low threshold")
        self.low_threshold_input.editingFinished.connect(self.update_thresholds)

        high_label = QLabel("High Threshold:")
        self.high_threshold_input = QLineEdit()
        self.high_threshold_input.setPlaceholderText("Enter high threshold")
        self.high_threshold_input.editingFinished.connect(self.update_thresholds)

        threshold_layout.addWidget(low_label)
        threshold_layout.addWidget(self.low_threshold_input)
        threshold_layout.addWidget(high_label)
        threshold_layout.addWidget(self.high_threshold_input)

        layout.addLayout(threshold_layout)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.setWindowTitle('CoinWatcher Settings')
        self.setWindowIcon(self.custom_icon)

        # System tray icon setup
        self.setup_tray_icon()

        # Timer for price updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_price)
        self.timer.start(self.interval * 1000)

        self.update_price()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.custom_icon)
        self.tray_icon.setToolTip("CoinWatcher")

        self.tray_menu = QMenu()
        self.price_action = QAction("Loading...", self)
        self.tray_menu.addAction(self.price_action)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show)
        self.tray_menu.addAction(settings_action)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        self.tray_menu.addAction(about_action)
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.tray_menu.hide)
        self.tray_menu.addAction(close_action)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToGlobal(event.position().toPoint()) - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def load_favorite_tickers(self):
        try:
            with open('favorite_tickers.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_favorite_tickers(self):
        with open('favorite_tickers.json', 'w') as f:
            json.dump(self.favorite_tickers, f)

    def add_favorite(self):
        ticker = self.ticker_input.text().lower()
        if ticker and ticker not in self.favorite_tickers:
            self.favorite_tickers.append(ticker)
            self.favorites_list.addItem(ticker)
            self.save_favorite_tickers()

    def remove_favorite(self):
        current_item = self.favorites_list.currentItem()
        if current_item:
            ticker = current_item.text()
            self.favorite_tickers.remove(ticker)
            self.favorites_list.takeItem(self.favorites_list.row(current_item))
            self.save_favorite_tickers()

    def select_favorite(self, item):
        self.ticker_input.setText(item.text())
        self.update_ticker()

    def tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.Context):
            self.show_menu()

    def show_menu(self):
        cursor_pos = QCursor.pos()
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        ideal_pos = QPoint(cursor_pos.x(), cursor_pos.y())
        menu_width = self.tray_menu.sizeHint().width()
        menu_height = self.tray_menu.sizeHint().height()

        if ideal_pos.x() + menu_width > screen_geometry.right():
            ideal_pos.setX(screen_geometry.right() - menu_width)
        if ideal_pos.y() + menu_height > screen_geometry.bottom():
            ideal_pos.setY(ideal_pos.y() - menu_height)

        self.tray_menu.popup(ideal_pos)

    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About Coin Watcher")
        about_dialog.setWindowIcon(self.custom_icon)

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 10, 80, 10)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(self.custom_icon.pixmap(64, 64))
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        about_text = "Coin Watcher\nRyon Shane Hall\nendorpheus@gmail.com\nversion 1.0"
        for line in about_text.split('\n'):
            label = QLabel(line)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(label)

        about_dialog.setLayout(layout)
        about_dialog.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        about_dialog.adjustSize()

        screen = QApplication.primaryScreen()
        if screen:
            center_point = screen.availableGeometry().center()
            frame_geometry = about_dialog.frameGeometry()
            frame_geometry.moveCenter(center_point)
            about_dialog.move(frame_geometry.topLeft())

        about_dialog.exec()

    def update_ticker(self):
        self.ticker = self.ticker_input.text().lower()
        self.update_price()

    def update_interval(self):
        self.interval = self.interval_slider.value()
        self.slider_value_label.setText(f"Current interval: {self.interval} seconds")
        self.timer.setInterval(self.interval * 1000)

    def update_thresholds(self):
        try:
            self.low_threshold = float(self.low_threshold_input.text()) if self.low_threshold_input.text() else None
            self.high_threshold = float(self.high_threshold_input.text()) if self.high_threshold_input.text() else None
        except ValueError:
            print("Invalid threshold value. Please enter numeric values.")

    def update_price(self):
        try:
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={self.ticker}&vs_currencies=usd")
            data = response.json()
            self.current_price = data[self.ticker]['usd']

            if self.previous_price is not None:
                change = self.current_price - self.previous_price
                percent_change = (change / self.previous_price) * 100
                arrow = "↑" if change >= 0 else "↓"
                change_text = f" {arrow} {abs(percent_change):.2f}%"
            else:
                change_text = ""

            price_text = f"{self.ticker.capitalize()}: ${self.current_price:.2f}{change_text}"
            self.price_action.setText(price_text)
            self.tray_icon.setToolTip(price_text)

            if self.low_threshold is not None and self.current_price <= self.low_threshold:
                self.set_icon_color("red")
            elif self.high_threshold is not None and self.current_price >= self.high_threshold:
                self.set_icon_color("green")
            else:
                self.set_icon_color("default")

            self.previous_price = self.current_price
        except Exception as e:
            error_text = f"Error: {str(e)}"
            self.price_action.setText(error_text)
            self.tray_icon.setToolTip("CoinWatcher")
            self.current_price = None
            self.previous_price = None

    def set_icon_color(self, color):
        if color == "default":
            self.tray_icon.setIcon(self.custom_icon)
        else:
            pixmap = QPixmap(self.icon_path)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            
            # Create a semi-transparent color (50% opacity)
            qcolor = QColor(color)
            qcolor.setAlpha(128)  # 128 is 50% of 255 (full opacity)
            
            painter.fillRect(pixmap.rect(), qcolor)
            painter.end()
            colored_icon = QIcon(pixmap)
            self.tray_icon.setIcon(colored_icon)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    crypto_ticker = CryptoTicker()
    sys.exit(app.exec())