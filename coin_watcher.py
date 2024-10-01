import sys
from PyQt6.QtWidgets import QApplication
from crypto_ticker import CryptoTicker

if __name__ == '__main__':
    app = QApplication(sys.argv)
    crypto_ticker = CryptoTicker()
    sys.exit(app.exec())
