import sqlite3
import hashlib
from PyQt6.QtWidgets import (QMainWindow, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

# We must import MainWindow here to open it on success
from ui.main_window import MainWindow

TEXT = {
    "en": {
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "switch_lang": "عربي"
    },
    "ar": {
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login": "تسجيل الدخول",
        "switch_lang": "English"
    }
}

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "en"
        self.old_pos = None 
        
        self.is_maximized_custom = False
        self.normal_geometry = QRect(0, 0, 400, 500) # Slightly wider for breathing room
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(self.normal_geometry)
        self.center_on_screen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0) 
        self.main_layout.setSpacing(0)
        central_widget.setLayout(self.main_layout)

        # Updated modern styling
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #ffffff; }
            QLineEdit {
                background-color: #2b2b2b; color: #ffffff;
                border: 1px solid #444444; border-radius: 8px;
                padding: 12px; font-size: 15px; min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #9b59b6; background-color: #333333; }
            QPushButton#primaryBtn {
                background-color: #9b59b6; color: white;
                border: none; border-radius: 8px; padding: 14px;
                font-size: 16px; font-weight: bold; min-width: 250px;
            }
            QPushButton#primaryBtn:hover { background-color: #8e44ad; }
            QPushButton#closeBtn { background-color: transparent; color: #ffffff; font-size: 16px; font-weight: bold; border: none; padding: 5px 10px; }
            QPushButton#closeBtn:hover { background-color: #ff4757; border-radius: 4px;}
            QPushButton#maxBtn { background-color: transparent; color: #ffffff; font-size: 16px; font-weight: bold; border: none; padding: 5px 10px; }
            QPushButton#maxBtn:hover { background-color: #5a5a5a; border-radius: 4px;}
            QPushButton#langBtn { background-color: transparent; color: #9b59b6; font-size: 14px; font-weight: bold; border: none; padding: 5px; }
            QPushButton#langBtn:hover { color: #ffffff; }
        """)

        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("background-color: #111111;") # Darker title bar
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)
        self.title_bar.setLayout(title_layout)

        self.lang_btn = QPushButton(TEXT[self.current_lang]["switch_lang"])
        self.lang_btn.setObjectName("langBtn")
        self.lang_btn.clicked.connect(self.toggle_language)
        title_layout.addWidget(self.lang_btn)

        title_layout.addStretch()

        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("maxBtn")
        self.max_btn.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)

        self.main_layout.addWidget(self.title_bar)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.setSpacing(25) # More breathing room
        self.content_widget.setLayout(self.content_layout)

        title_label = QLabel("flwr")
        title_label.setStyleSheet("font-size: 42px; font-weight: bold; color: #9b59b6; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title_label)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText(TEXT[self.current_lang]["username"])
        # MAGIC LINE 1: Trigger login on Enter key
        self.user_input.returnPressed.connect(self.attempt_login) 
        self.content_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText(TEXT[self.current_lang]["password"])
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        # MAGIC LINE 2: Trigger login on Enter key
        self.pass_input.returnPressed.connect(self.attempt_login)
        self.content_layout.addWidget(self.pass_input)

        self.login_btn = QPushButton(TEXT[self.current_lang]["login"])
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.clicked.connect(self.attempt_login) 
        self.content_layout.addWidget(self.login_btn)

        self.main_layout.addWidget(self.content_widget, 1)

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def toggle_maximize(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200) 
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart) 
        self.anim.setStartValue(self.geometry())

        if self.is_maximized_custom:
            self.anim.setEndValue(self.normal_geometry)
            self.is_maximized_custom = False
            self.max_btn.setText("□")
        else:
            self.normal_geometry = self.geometry()
            screen_geom = self.screen().availableGeometry()
            self.anim.setEndValue(screen_geom)
            self.is_maximized_custom = True
            self.max_btn.setText("❐")

        self.anim.start()

    def toggle_language(self):
        self.current_lang = "ar" if self.current_lang == "en" else "en"
        self.user_input.setPlaceholderText(TEXT[self.current_lang]["username"])
        self.pass_input.setPlaceholderText(TEXT[self.current_lang]["password"])
        self.login_btn.setText(TEXT[self.current_lang]["login"])
        self.lang_btn.setText(TEXT[self.current_lang]["switch_lang"])

        if self.current_lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def attempt_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        
        if not username or not password:
            self.show_popup("Error", "Please enter both username and password.", is_error=True)
            return

        hashed_input = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('store_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            db_password, role = result
            if db_password == hashed_input:
                self.main_window = MainWindow(username, role)
                self.main_window.show()
                self.close() 
            else:
                self.show_popup("Error", "Incorrect password.", is_error=True)
        else:
            self.show_popup("Error", "User not found.", is_error=True)

    def show_popup(self, title, message, is_error=False):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; color: white; font-family: 'Segoe UI', sans-serif;}
            QLabel { color: white; min-width: 200px; font-size: 14px; }
            QPushButton { background-color: #9b59b6; color: white; border-radius: 4px; padding: 5px 15px; }
        """)
        if is_error:
            msg.setIcon(QMessageBox.Icon.Warning)
        else:
            msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 40:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and not self.is_maximized_custom:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None