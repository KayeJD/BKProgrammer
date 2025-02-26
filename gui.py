import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QGridLayout, QHBoxLayout,
)

from controllerTest import Controller, ListProgrammer  # controllerTest: fake controller

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = Controller()
        self.list_programmer = ListProgrammer(self.controller)

        self.setWindowTitle("BK Programmer")
        self.setFixedSize(QSize(1000, 700))
        # layout = QVBoxLayout()
        layout = QGridLayout()

        # layout.addWidget(QLabel("Range: "))
        #
        # layout.addWidget(QSpinBox(), 0, 0)
        # layout.addWidget(QDoubleSpinBox(), 1, 0)
        # layout.addWidget(QDoubleSpinBox(), 1, 1)
        # layout.addWidget(QDoubleSpinBox(), 2, 1)

        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()

        layout2.addWidget(QDoubleSpinBox())
        layout2.addWidget(QDoubleSpinBox())
        layout2.addWidget(QDoubleSpinBox())

        layout1.addLayout(layout2)

        layout1.addWidget(QSpinBox())

        layout3.addWidget(QSpinBox())
        layout3.addWidget(QSpinBox())

        layout1.addLayout(layout3)

        # widgets = [
        #     QCheckBox,
        #     QComboBox,
        #     QDateEdit,
        #     QDateTimeEdit,
        #     QDial,
        #     QDoubleSpinBox,
        #     QFontComboBox,
        #     QLCDNumber,
        #     QLabel,
        #     QLineEdit,
        #     QProgressBar,
        #     QPushButton,
        #     QRadioButton,
        #     QSlider,
        #     QSpinBox,
        #     QTimeEdit,
        # ]
        # for w in widgets:
        #     layout.addWidget(w())

        # layout.addWidget(QDoubleSpinBox())
        # layout.addWidget(QSpinBox())

        submit_btn = QPushButton("Submit")

        widget = QWidget()
        widget.setLayout(layout1)

        self.setCentralWidget(widget)

    def connect_to_instrument(self):
        self.controller.connect()
        # self.status_label.setText(self.controller.check_connection())

    # def load_parameters(self):
        # params = self.list_programmer.get_list_params("test_params.txt")
        # self.result_label.setText(param_display)
