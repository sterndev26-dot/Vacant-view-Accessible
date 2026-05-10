from PyQt6.QtWidgets import QWidget, QApplication, QLineEdit, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
import sys

class RtlInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Input")
        self.setGeometry(100, 100, 300, 80)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.line_edit.setPlaceholderText("Enter text")
        layout.addWidget(self.line_edit)

        btn = QPushButton("OK")
        btn.clicked.connect(self.on_ok)
        layout.addWidget(btn)

        self.setLayout(layout)

    def on_ok(self):
        print(self.line_edit.text())
        QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RtlInputWidget()
    w.show()
    sys.exit(app.exec())
