import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Reg_Window import Reg_Window
from Login_Window import Login_Window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(600, 400, 300, 200)

        login = QPushButton("login",self)
        login.move(110, 60)
        login.clicked.connect(self.login_button)

        reg = QPushButton("Face_id 등록",self)
        reg.move(110, 100)
        reg.clicked.connect(self.reg_button)

    def login_button(self):
        win = Login_Window()
        r = win.showModal()

    def reg_button(self):
        win = Reg_Window()
        r = win.showModal()

    def show(self):
        super().show()
