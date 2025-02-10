#!/usr/bin/env python3
"""
PyQt5 GUI Calculator with many Casio fx-50FH II functions.
"""

import sys
import math
import random
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)
from PyQt5.QtGui import QFont


# --- Helper Functions ---
def recip(x):
    return 1 / x


def cube(x):
    return x**3


def square(x):
    return x**2


def cuberoot(x):
    return x ** (1 / 3)


def ten_pow(x):
    return 10**x


def e_pow(x):
    return math.e**x


def nPr(n, r):
    if hasattr(math, "perm"):  # Python >= 3.8
        return math.perm(n, r)
    return math.factorial(n) // math.factorial(n - r)


def nCr(n, r):
    if hasattr(math, "comb"):  # Python >= 3.8
        return math.comb(n, r)
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


def toPolar(z):
    if isinstance(z, complex):
        return (abs(z), math.degrees(math.atan2(z.imag, z.real)))
    return (abs(z), 0)


def toRec(t):
    r, theta = t
    return r * (math.cos(math.radians(theta)) + 1j * math.sin(math.radians(theta)))


def root(x, n):
    return x ** (1 / n)


def power(x, y):
    return x**y


# --- Allowed names ---
ALLOWED_NAMES = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "arcsin": math.asin,
    "arccos": math.acos,
    "arctan": math.atan,
    "log": lambda x: math.log10(x),
    "ln": math.log,
    "factorial": math.factorial,
    "cube": cube,
    "square": square,
    "cuberoot": cuberoot,
    "ten_pow": ten_pow,
    "e_pow": e_pow,
    "recip": recip,
    "nPr": nPr,
    "nCr": nCr,
    "toPolar": toPolar,
    "toRec": toRec,
    "root": root,
    "power": power,
    "pi": math.pi,
    "e": math.e,
    "random": lambda: random.random(),
}


# --- Mapping for insertion strings ---
INSERTION_MAP = {
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "arcsin": "arcsin(",
    "arccos": "arccos(",
    "arctan": "arctan(",
    "log": "log(",
    "ln": "ln(",
    "sqrt": "sqrt(",
    "factorial": "factorial(",
    "cube": "cube(",
    "square": "square(",
    "cuberoot": "cuberoot(",
    "10^x": "ten_pow(",
    "e^x": "e_pow(",
    "^-1": "recip(",
    "nPr": "nPr(",
    "nCr": "nCr(",
    "Pol": "toPolar(",
    "Rec": "toRec(",
    "root": "root(",
    "power": "power(",
}


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Casio fx-50FH II GUI Calculator")
        self.setGeometry(100, 100, 600, 700)
        self.last_ans = ""
        self.expression = ""
        self.initUI()

    def initUI(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # Layouts
        main_layout = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)
        self.display.setFont(QFont("Arial", 16))
        main_layout.addWidget(self.display)

        grid_layout = QGridLayout()

        # Define button labels row by row
        buttons = [
            ["HEX", "BIN", "DEC", "OCT", "CLEAR", "DELETE"],
            ["7", "8", "9", "/", "nPr", "nCr"],
            ["4", "5", "6", "*", "Pol", "Rec"],
            ["1", "2", "3", "-", "(", ")"],
            ["0", ".", "pi", "+", "ANS", "EXE"],
            ["factorial", "^-1", "cuberoot", "cube", "square", "root"],
            ["sqrt", "power", "log", "10^x", "ln", "e^x"],
            ["e", "sin", "cos", "tan", "arcsin", "arccos"],
            ["arctan", "csc", "sec", "cot", "i", "random"],
        ]

        red_buttons = ["EXE", "ANS", "CLEAR", "DELETE"]

        # Create buttons
        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                button = QPushButton(btn_text)
                button.setFixedSize(80, 50)
                button.setFont(QFont("Arial", 10, QFont.Bold))
                if btn_text in red_buttons:
                    button.setStyleSheet("color: red;")
                button.clicked.connect(self.buttonClicked)
                grid_layout.addWidget(button, row_idx, col_idx)

        main_layout.addLayout(grid_layout)
        widget.setLayout(main_layout)

    def buttonClicked(self):
        sender = self.sender()
        btn_text = sender.text()

        if btn_text == "CLEAR":
            self.expression = ""
        elif btn_text == "DELETE":
            self.expression = self.expression[:-1]
        elif btn_text == "EXE":
            self.evaluateExpression()
        elif btn_text == "ANS":
            self.expression += str(self.last_ans)
        elif btn_text in ("HEX", "BIN", "DEC", "OCT"):
            try:
                value = int(float(self.last_ans))
                if btn_text == "HEX":
                    self.expression = hex(value)
                elif btn_text == "BIN":
                    self.expression = bin(value)
                elif btn_text == "DEC":
                    self.expression = str(value)
                elif btn_text == "OCT":
                    self.expression = oct(value)
                self.last_ans = self.expression
            except Exception:
                self.showError("No valid integer stored in ANS for conversion.")
        elif btn_text == "i":
            self.expression += "j"
        elif btn_text == "random":
            self.expression += "random()"
        elif btn_text in ("csc", "sec", "cot"):
            self.expression += btn_text + "("
            if "csc" not in ALLOWED_NAMES:
                ALLOWED_NAMES["csc"] = lambda x: 1 / math.sin(x)
            if "sec" not in ALLOWED_NAMES:
                ALLOWED_NAMES["sec"] = lambda x: 1 / math.cos(x)
            if "cot" not in ALLOWED_NAMES:
                ALLOWED_NAMES["cot"] = lambda x: 1 / math.tan(x)
        elif btn_text in INSERTION_MAP:
            self.expression += INSERTION_MAP[btn_text]
        else:
            self.expression += btn_text

        self.display.setText(self.expression)

    def evaluateExpression(self):
        try:
            open_parens = self.expression.count("(")
            close_parens = self.expression.count(")")
            self.expression += ")" * (open_parens - close_parens)

            result = eval(self.expression, {"__builtins__": {}}, ALLOWED_NAMES)
            self.last_ans = result
            self.expression = str(result)
            self.display.setText(self.expression)
        except Exception as e:
            self.showError("Error: " + str(e))

    def showError(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
