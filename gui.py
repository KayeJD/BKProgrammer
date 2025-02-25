import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BK Programmer")
        button = QPushButton("Press Me!")
        self.setFixedSize(QSize(1000, 700))

        # Set the central widget of the Window.
        # self.setCentralWidget(button)

def on_button_clicked():
    alert = QMessageBox()
    alert.setText('You clicked the button!')
    alert.exec()



app = QApplication(sys.argv)

window = MainWindow()
window.button.clicked.connect(on_button_clicked)
window.show()

app.exec()