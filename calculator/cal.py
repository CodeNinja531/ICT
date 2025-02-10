#!/usr/bin/env python3
"""
PyQt5 GUI Calculator with many Casio fx-50FH II functions.
Buttons include:
  factorial, ^-1, cuberoot, cube, +, -, *, /, sqrt, square, root,
  power, log, 10^x, ln, e^x, e, sin, cos, tan, arcsin, arccos, arctan,
  csc, sec, cot, (, ), i, HEX, BIN, DEC, OCT, 0-9, ., pi, random,
  DELETE, CLEAR, nPr, nCr, Pol, Rec, ANS, EXE.

Run this program with PyQt5 installed.
"""

import sys
import math
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)


# --- Helper Functions used in eval ---
def recip(x):
    return 1 / x

def cube(x):
    return x ** 3

def square(x):
    return x ** 2

def cuberoot(x):
    return x ** (1 / 3)

def ten_pow(x):
    return 10 ** x

def e_pow(x):
    return math.e ** x

def nPr(n, r):
    # Uses math.perm if available (Python>=3.8)
    if hasattr(math, "perm"):
        return math.perm(n, r)
    else:
        return math.factorial(n) // math.factorial(n - r)

def nCr(n, r):
    # Uses math.comb if available (Python>=3.8)
    if hasattr(math, "comb"):
        return math.comb(n, r)
    else:
        return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

def toPolar(z):
    # Returns (r, theta-in-degrees) for complex z.
    if isinstance(z, complex):
        return (abs(z), math.degrees(math.atan2(z.imag, z.real)))
    else:
        return (abs(z), 0)

def toRec(t):
    # Expects a tuple (r, theta in degrees); return the complex number.
    r, theta = t
    return r * (math.cos(math.radians(theta)) + 1j * math.sin(math.radians(theta)))

def root(x, n):
    return x ** (1 / n)

def power(x, y):
    return x ** y


# --- Allowed names for eval ---
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
    "random": lambda: random.random()
}


# --- Mapping for insertion strings ---
# Some buttons should insert a function call (with an open parenthesis).
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
    "root": "root(",   # expects two arguments: root(x, n)
    "power": "power(", # expects two arguments: power(x, y)
}


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Casio fx-50FH II GUI Calculator")
        self.setGeometry(100, 100, 500, 600)
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
        self.display.setFixedHeight(50)
        main_layout.addWidget(self.display)

        grid_layout = QGridLayout()

        # Define the button labels row by row.
        buttons = [
            ["HEX", "BIN", "DEC", "OCT", "CLEAR", "DELETE"],
            ["7", "8", "9", "/", "nPr", "nCr"],
            ["4", "5", "6", "*", "Pol", "Rec"],
            ["1", "2", "3", "-", "(", ")"],
            ["0", ".", "pi", "+", "ANS", "EXE"],
            ["factorial", "^-1", "cuberoot", "cube", "square", "root"],
            ["sqrt", "power", "log", "10^x", "ln", "e^x"],
            ["e", "sin", "cos", "tan", "arcsin", "arccos"],
            ["arctan", "csc", "sec", "cot", "i", "random"]
        ]

        # The list of button texts to be displayed in red.
        red_buttons = ["EXE", "ANS", "CLEAR", "DELETE"]

        # Create buttons and add to grid.
        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                button = QPushButton(btn_text)
                button.setFixedSize(80, 50)
                # Format specific buttons with red text.
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
            self.display.setText(self.expression)
            return
        elif btn_text == "DELETE":
            # Check if the end of expression matches any inserted function call
            removed = False
            # Sort the insertion strings by length (longest first) to catch longer matches first.
            for key, ins_str in sorted(INSERTION_MAP.items(), key=lambda x: -len(x[1])):
                if self.expression.endswith(ins_str):
                    self.expression = self.expression[:-len(ins_str)]
                    removed = True
                    break
            if not removed:
                # If no function substring match, delete last character.
                self.expression = self.expression[:-1]
            self.display.setText(self.expression)
            return
        elif btn_text == "EXE":
            self.evaluateExpression()
            return
        elif btn_text == "ANS":
            # Insert the last answer into the expression.
            self.expression += str(self.last_ans)
            self.display.setText(self.expression)
            return
        elif btn_text in ("HEX", "BIN", "DEC", "OCT"):
            # Convert last answer (if integer) to the selected numeral system.
            try:
                value = int(float(self.last_ans))
            except Exception:
                self.showError("No valid integer stored in ANS for conversion.")
                return

            if btn_text == "HEX":
                converted = hex(value)
            elif btn_text == "BIN":
                converted = bin(value)
            elif btn_text == "DEC":
                converted = str(value)
            elif btn_text == "OCT":
                converted = oct(value)
            self.expression = converted
            self.display.setText(self.expression)
            self.last_ans = converted
            return
        elif btn_text == "i":
            # For imaginary unit, insert Python's 'j'
            self.expression += "j"
            self.display.setText(self.expression)
            return
        elif btn_text == "random":
            # Insert function call for random.
            self.expression += "random()"
            self.display.setText(self.expression)
            return
        elif btn_text in ("csc", "sec", "cot"):
            # Define these in terms of sin, cos, tan.
            # csc(x) = 1/sin(x), sec(x)=1/cos(x), cot(x)=1/tan(x)
            self.expression += btn_text + "("
            if "csc" not in ALLOWED_NAMES:
                ALLOWED_NAMES["csc"] = lambda x: 1 / math.sin(x)
            if "sec" not in ALLOWED_NAMES:
                ALLOWED_NAMES["sec"] = lambda x: 1 / math.cos(x)
            if "cot" not in ALLOWED_NAMES:
                ALLOWED_NAMES["cot"] = lambda x: 1 / math.tan(x)
            return

        # If the button text is one of our functions that require an open parenthesis:
        if btn_text in INSERTION_MAP:
            self.expression += INSERTION_MAP[btn_text]
        else:
            # For numbers, operators, parentheses, pi, e, etc.
            if btn_text == "pi":
                self.expression += "pi"
            elif btn_text == "e":
                self.expression += "e"
            else:
                self.expression += btn_text
        self.display.setText(self.expression)

    def evaluateExpression(self):
        try:
            # Evaluate the expression using eval and our allowed names.
            # Provide a safe context with no builtins.
            result = eval(self.expression, {"__builtins__": {}}, ALLOWED_NAMES)
            self.display.setText(str(result))
            self.last_ans = result
            self.expression = str(result)
        except Exception as e:
            self.showError("Error: " + str(e))
            # Do not clear the existing input on error.

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

