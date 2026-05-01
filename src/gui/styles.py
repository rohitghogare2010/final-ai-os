
STYLESHEET = """
QMainWindow {
    background-color: #050505;
}

QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
}

QStackedWidget {
    background: rgba(20, 20, 25, 180);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 10);
}

QPushButton {
    background-color: rgba(30, 30, 40, 150);
    border: 1px solid rgba(0, 255, 255, 50);
    border-radius: 8px;
    padding: 10px;
    color: #00ffff;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QPushButton:hover {
    background-color: rgba(0, 255, 255, 30);
    border: 1px solid #00ffff;
    box-shadow: 0 0 15px rgba(0, 255, 255, 150);
}

QPushButton#sidebar_btn {
    text-align: left;
    border: none;
    background: transparent;
    padding-left: 15px;
    color: #888;
}

QPushButton#sidebar_btn:hover {
    color: #00ffff;
    background: rgba(0, 255, 255, 10);
}

QPushButton#sidebar_btn[active="true"] {
    color: #00ffff;
    background: rgba(0, 255, 255, 20);
    border-left: 3px solid #00ffff;
}

QLineEdit, QTextEdit {
    background-color: rgba(15, 15, 20, 200);
    border: 1px solid rgba(0, 255, 255, 30);
    border-radius: 5px;
    padding: 8px;
    color: #fff;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #00ffff;
}

QLabel {
    color: #00ffff;
    font-weight: 600;
}

QComboBox {
    background-color: rgba(30, 30, 40, 200);
    border: 1px solid rgba(0, 255, 255, 30);
    border-radius: 5px;
    padding: 5px;
    color: #fff;
}

QComboBox::drop-down {
    border: none;
}

QProgressBar {
    border: 1px solid rgba(0, 255, 255, 30);
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #00ffff;
}

#sidebar_widget {
    background-color: rgba(10, 10, 15, 255);
    border-right: 1px solid rgba(255, 255, 255, 10);
}

#header_label {
    font-size: 18px;
    font-weight: bold;
    color: #fff;
    margin-bottom: 20px;
    padding: 10px;
}
"""
