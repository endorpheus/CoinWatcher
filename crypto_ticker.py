import os
import json
import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QSlider, QMenu, QSystemTrayIcon, QPushButton, QListWidget, 
                             QColorDialog, QListWidgetItem, QDialog, QSizePolicy, 
                             QApplication)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QCursor, QColor, QPainter, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QPoint
from floating_window import FloatingPriceWindow

VERSION = '1.0.2'

class ColorSelectionDialog(QDialog):
    def __init__(self, parent=None, bg_color=None, fg_color=None):
        super().__init__(parent)
        self.bg_color = bg_color or QColor(75, 0, 130)
        self.fg_color = fg_color or QColor(255, 255, 255)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Color:")
        self.bg_button = QPushButton()
        self.bg_button.setStyleSheet(f"background-color: {self.bg_color.name()}; min-width: 100px; min-height: 30px;")
        self.bg_button.clicked.connect(lambda: self.choose_color('bg'))
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_button)
        layout.addLayout(bg_layout)

        fg_layout = QHBoxLayout()
        fg_label = QLabel("Foreground Color:")
        self.fg_button = QPushButton()
        self.fg_button.setStyleSheet(f"background-color: {self.fg_color.name()}; min-width: 100px; min-height: 30px;")
        self.fg_button.clicked.connect(lambda: self.choose_color('fg'))
        fg_layout.addWidget(fg_label)
        fg_layout.addWidget(self.fg_button)
        layout.addLayout(fg_layout)

        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        self.setLayout(layout)
        self.setWindowTitle("Choose Colors")

    def choose_color(self, color_type):
        color = QColorDialog.getColor()
        if color.isValid():
            if color_type == 'bg':
                self.bg_color = color
                self.bg_button.setStyleSheet(f"background-color: {color.name()}; min-width: 100px; min-height: 30px;")
            else:
                self.fg_color = color
                self.fg_button.setStyleSheet(f"background-color: {color.name()}; min-width: 100px; min-height: 30px;")

class CryptoTicker(QWidget):
    def __init__(self):
        super().__init__()
        self.ticker = "bitcoin"
        self.interval = 60
        self.current_price = None
        self.previous_price = None
        self.favorite_tickers = self.load_favorite_tickers()
        self.floating_window = None
        self.initUI()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.dragging = False
        self.offset = QPoint()

    def initUI(self):
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons/coin.png')
        self.custom_icon = QIcon(self.icon_path)

        layout = QVBoxLayout()

        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        self.ticker_input = QLineEdit(self.ticker)
        self.ticker_input.editingFinished.connect(self.update_ticker)
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_input)
        layout.addLayout(ticker_layout)

        self.favorites_list = QListWidget()
        self.update_favorites_list()
        self.favorites_list.itemClicked.connect(self.select_favorite)
        layout.addWidget(self.favorites_list)

        fav_buttons_layout = QHBoxLayout()
        add_fav_button = QPushButton("Add Favorite")
        add_fav_button.clicked.connect(self.add_favorite)
        edit_fav_button = QPushButton("Edit Favorite")
        edit_fav_button.clicked.connect(self.edit_favorite)
        remove_fav_button = QPushButton("Remove Favorite")
        remove_fav_button.clicked.connect(self.remove_favorite)
        fav_buttons_layout.addWidget(add_fav_button)
        fav_buttons_layout.addWidget(edit_fav_button)
        fav_buttons_layout.addWidget(remove_fav_button)
        layout.addLayout(fav_buttons_layout)

        # slider layout 2
        interval_layout = QVBoxLayout()
        #interval_label = QLabel(f"Interval: {self.interval} seconds")
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(30)
        self.interval_slider.setMaximum(1500)
        self.interval_slider.setValue(self.interval)
        self.interval_slider.setTickInterval(100)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.valueChanged.connect(self.update_interval)

        self.slider_value_label = QLabel(f"Interval: {self.interval} seconds")
        
        interval_layout.addWidget(self.slider_value_label)
        #interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        
        layout.addLayout(interval_layout)

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

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.setWindowTitle('CoinWatcher Settings')
        self.setWindowIcon(self.custom_icon)

        self.setup_tray_icon()

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
        self.price_action.triggered.connect(self.toggle_floating_window)
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
        quit_action.triggered.connect(QApplication.instance().quit)  # Modified line
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)  # Set the context menu for the tray icon
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def toggle_floating_window(self):
        if self.floating_window is None:
            self.floating_window = FloatingPriceWindow()
            self.floating_window.setWindowIcon(self.custom_icon)
            self.floating_window.update_price(self.price_action.text())
            self.floating_window.show()
        else:
            self.floating_window.setVisible(not self.floating_window.isVisible())

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
            return {}

    def save_favorite_tickers(self):
        with open('favorite_tickers.json', 'w') as f:
            json.dump(self.favorite_tickers, f, indent=4) # keep it readable

    def add_favorite(self):
        ticker = self.ticker_input.text().lower()
        if ticker and ticker not in self.favorite_tickers:
            color_dialog = ColorSelectionDialog(self)
            if color_dialog.exec() == QDialog.DialogCode.Accepted:
                self.favorite_tickers[ticker] = {
                    'color': color_dialog.bg_color.name(),
                    'text_color': color_dialog.fg_color.name(),
                    'low_threshold': None,
                    'high_threshold': None
                }
                self.update_favorites_list()
                self.save_favorite_tickers()
                if self.floating_window and self.ticker == ticker:
                    self.update_floating_window()

    def edit_favorite(self):
        current_item = self.favorites_list.currentItem()
        if current_item:
            ticker = current_item.text()
            data = self.favorite_tickers[ticker]
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit {ticker}")
            layout = QVBoxLayout()

            color_button = QPushButton("Change Colors")
            color_button.clicked.connect(lambda: self.change_colors(ticker))
            layout.addWidget(color_button)

            low_threshold_input = QLineEdit(str(data['low_threshold']) if data['low_threshold'] else "")
            high_threshold_input = QLineEdit(str(data['high_threshold']) if data['high_threshold'] else "")
            layout.addWidget(QLabel("Low Threshold:"))
            layout.addWidget(low_threshold_input)
            layout.addWidget(QLabel("High Threshold:"))
            layout.addWidget(high_threshold_input)

            save_button = QPushButton("Save")
            save_button.clicked.connect(lambda: self.save_favorite_changes(ticker, low_threshold_input.text(), high_threshold_input.text(), dialog))
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()

    def remove_favorite(self):
        current_item = self.favorites_list.currentItem()
        if current_item:
            ticker = current_item.text()
            del self.favorite_tickers[ticker]
            self.update_favorites_list()
            self.save_favorite_tickers()

    def select_favorite(self, item):
        ticker = item.text()
        self.ticker_input.setText(ticker)
        self.update_ticker()
        if self.floating_window:
            self.update_floating_window()

    def change_colors(self, ticker):
        data = self.favorite_tickers[ticker]
        color_dialog = ColorSelectionDialog(self, QColor(data['color']), QColor(data['text_color']))
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            self.favorite_tickers[ticker]['color'] = color_dialog.bg_color.name()
            self.favorite_tickers[ticker]['text_color'] = color_dialog.fg_color.name()
            self.update_favorites_list()
            self.save_favorite_tickers()
            if self.floating_window and self.ticker == ticker:
                self.update_floating_window()

    def save_favorite_changes(self, ticker, low_threshold, high_threshold, dialog):
        try:
            self.favorite_tickers[ticker]['low_threshold'] = float(low_threshold) if low_threshold else None
            self.favorite_tickers[ticker]['high_threshold'] = float(high_threshold) if high_threshold else None
            self.save_favorite_tickers()
            if self.floating_window and self.ticker == ticker:
                self.update_floating_window()
            dialog.accept()
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            tickers = list(self.favorite_tickers.keys())
            current_index = tickers.index(self.ticker)
            next_index = (current_index + 1) % len(tickers)
            self.ticker = tickers[next_index]
            self.ticker_input.setText(self.ticker)
            self.update_price()
            self.update_floating_window()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self.show_menu()

    def show_menu(self):
        cursor_pos = QCursor.pos()
        screen = self.screen()
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
        about_dialog.setWindowTitle("About CoinWatcher")
        about_dialog.setWindowIcon(self.custom_icon)

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 10, 80, 10)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(self.custom_icon.pixmap(64, 64))
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        about_text = f"CoinWatcher\nRyon Shane Hall\nendorpheus@gmail.com\nVersion: {VERSION}"
        for line in about_text.split('\n'):
            label = QLabel(line)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(label)

        about_dialog.setLayout(layout)
        about_dialog.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        about_dialog.adjustSize()

        screen = self.screen()
        if screen:
            center_point = screen.availableGeometry().center()
            frame_geometry = about_dialog.frameGeometry()
            frame_geometry.moveCenter(center_point)
            about_dialog.move(frame_geometry.topLeft())

        about_dialog.exec()

    def update_favorites_list(self):
        self.favorites_list.clear()
        for ticker, data in self.favorite_tickers.items():
            item = QListWidgetItem(ticker)
            item.setForeground(QColor(data['color']))
            self.favorites_list.addItem(item)

    def update_ticker(self):
        self.ticker = self.ticker_input.text().lower()
        self.update_price()
        self.update_floating_window()

    def update_interval(self):
        self.interval = self.interval_slider.value()
        self.slider_value_label.setText(f"Interval: {self.interval} seconds")
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

            if self.floating_window and self.floating_window.isVisible():
                self.floating_window.update_price(price_text)

            if self.ticker in self.favorite_tickers:
                data = self.favorite_tickers[self.ticker]
                if data['low_threshold'] is not None and self.current_price <= data['low_threshold']:
                    self.set_icon_color(data['color'], 0.5)
                elif data['high_threshold'] is not None and self.current_price >= data['high_threshold']:
                    self.set_icon_color(data['color'], 1)
                else:
                    self.set_icon_color(data['color'], 0.2)
            else:
                self.set_icon_color("default")

            self.previous_price = self.current_price

        except Exception as e:
            error_text = f"Error: {str(e)}"
            self.price_action.setText(error_text)
            self.tray_icon.setToolTip("CoinWatcher")
            self.current_price = None
            self.previous_price = None

    def set_icon_color(self, color, opacity=1):
        if color == "default":
            self.tray_icon.setIcon(self.custom_icon)
        else:
            pixmap = QPixmap(self.icon_path)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)

            qcolor = QColor(color)
            qcolor.setAlphaF(opacity)

            painter.fillRect(pixmap.rect(), qcolor)
            painter.end()
            colored_icon = QIcon(pixmap)
            self.tray_icon.setIcon(colored_icon)

    def update_floating_window(self):
        if self.floating_window:
            if self.ticker in self.favorite_tickers:
                data = self.favorite_tickers[self.ticker]
                self.floating_window.set_background_color(data['color'])
                self.floating_window.set_text_color(data.get('text_color', '#FFFFFF'))
            else:
                self.floating_window.set_background_color(QColor(75, 0, 130))
                self.floating_window.set_text_color('#FFFFFF')
            self.floating_window.update_price(self.price_action.text())

    def toggle_floating_window(self):
        if self.floating_window is None:
            self.floating_window = FloatingPriceWindow()
            self.floating_window.setWindowIcon(self.custom_icon)
            self.update_floating_window()
            self.floating_window.update_price(self.price_action.text())
            self.floating_window.show()
        else:
            self.floating_window.setVisible(not self.floating_window.isVisible())

