import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep running in tray
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
