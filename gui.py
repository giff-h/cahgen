from pdf_gen import PackProfile, WhiteCardWriter, BlackCardWriter, CardBackWriter

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class CahGen(QWidget):
    def __init__(self):
        super().__init__()

        self.main_screen()

    def main_screen(self):
        self.setGeometry(100, 100, 1000, 700)
        self.show()


def run():
    app = QApplication(sys.argv)
    window = CahGen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
