import sys
import os
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QMenu, QSystemTrayIcon, QSizePolicy
from PyQt6.QtGui import QIcon, QAction, QPixmap, QCursor, QScreen
from PyQt6.QtCore import Qt, QTimer, QPoint

class CryptoTicker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.ticker = "bitcoin"
        self.interval = 300
        self.current_price = None

        # Load custom icon
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'coin.png')
        self.custom_icon = QIcon(self.icon_path)

        layout = QVBoxLayout()

        # Ticker input
        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        self.ticker_input = QLineEdit(self.ticker)
        self.ticker_input.editingFinished.connect(self.update_ticker)
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_input)
        layout.addLayout(ticker_layout)

        # Interval slider
        interval_layout = QVBoxLayout()
        interval_label = QLabel("Interval (seconds):")
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(300)
        self.interval_slider.setMaximum(1200)
        self.interval_slider.setValue(self.interval)
        self.interval_slider.setTickInterval(100)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.valueChanged.connect(self.update_interval)
        
        # Slider value display
        self.slider_value_label = QLabel(f"Current interval: {self.interval} seconds")
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.slider_value_label)
        layout.addLayout(interval_layout)

        self.setLayout(layout)
        self.setWindowTitle('Crypto Ticker Settings')
        
        # Set window icon
        self.setWindowIcon(self.custom_icon)

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.custom_icon)
        self.tray_icon.setToolTip("CoinWatcher")
        
        # Create menu for left-click
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
        
        # Set left-click to open menu
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        self.tray_icon.show()

        # Set up timer for price updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_price)
        self.timer.start(self.interval * 1000)

        self.update_price()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.show_menu()
        elif reason == QSystemTrayIcon.ActivationReason.Context:  # Right click
            self.show_menu()

    def show_menu(self):
        # Get the global position of the cursor
        cursor_pos = QCursor.pos()
        
        # Get the available screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Calculate the ideal position for the menu
        ideal_pos = QPoint(cursor_pos.x(), cursor_pos.y())
        
        # Adjust if the menu would go off the right edge of the screen
        menu_width = self.tray_menu.sizeHint().width()
        if ideal_pos.x() + menu_width > screen_geometry.right():
            ideal_pos.setX(screen_geometry.right() - menu_width)
        
        # Adjust if the menu would go off the bottom edge of the screen
        menu_height = self.tray_menu.sizeHint().height()
        if ideal_pos.y() + menu_height > screen_geometry.bottom():
            ideal_pos.setY(ideal_pos.y() - menu_height)
        
        # Show the menu at the calculated position
        self.tray_menu.popup(ideal_pos)

    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About KDE Coin Watcher")
        about_dialog.setWindowIcon(self.custom_icon)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 10, 80, 10)  # Left, Top, Right, Bottom
        layout.setSpacing(10)  # Add some spacing between widgets
        
        # Add icon
        icon_label = QLabel()
        icon_label.setPixmap(self.custom_icon.pixmap(64, 64))
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Add about text
        about_text = "KDE Coin Watcher\nRyon Shane Hall\nendorpheus@gmail.com\nversion 1.0"
        for line in about_text.split('\n'):
            label = QLabel(line)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(label)
        
        about_dialog.setLayout(layout)
        
        # Set size policy to adjust to content
        about_dialog.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        # Adjust size to fit content
        about_dialog.adjustSize()
        
        # Center the dialog on the screen
        screen = QApplication.primaryScreen()
        if screen:
            center_point = screen.availableGeometry().center()
            frame_geometry = about_dialog.frameGeometry()
            frame_geometry.moveCenter(center_point)
            about_dialog.move(frame_geometry.topLeft())
        
        # Show the dialog
        about_dialog.exec()

    def update_ticker(self):
        self.ticker = self.ticker_input.text().lower()
        self.update_price()

    def update_interval(self):
        self.interval = self.interval_slider.value()
        self.slider_value_label.setText(f"Current interval: {self.interval} seconds")
        self.timer.setInterval(self.interval * 1000)

    def update_price(self):
        try:
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={self.ticker}&vs_currencies=usd")
            data = response.json()
            self.current_price = data[self.ticker]['usd']
            price_text = f"{self.ticker.capitalize()}: ${self.current_price:.2f}"
            self.price_action.setText(price_text)
            self.tray_icon.setToolTip(price_text)
        except Exception as e:
            error_text = f"Error: {str(e)}"
            self.price_action.setText(error_text)
            self.tray_icon.setToolTip("CoinWatcher")
            self.current_price = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    crypto_ticker = CryptoTicker()
    sys.exit(app.exec())