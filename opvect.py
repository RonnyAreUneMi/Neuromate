from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from sympy import symbols, sqrt, pretty

class CalculadoraVectores(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculadora de Vectores Neuromate")
        self.setGeometry(100, 100, 600, 400)

        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
            }

            QLabel {
                font-weight: bold;
                margin: 10px 0 5px;
                color: #003366;
            }

            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ff0000;
                border-radius: 8px;
                padding: 8px;
                width: 150px;
            }

            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ff0000;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton {
                background-color: #003366;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }

            QPushButton:hover {
                background-color: #004c99;
            }

            QPushButton#salir_button {
                background-color: #ff0000;
                color: white;
            }

            QPushButton#salir_button:hover {
                background-color: #ff6666;
            }
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.operacion_label = QLabel("Calculadora de Vectores Neuromate")
        self.layout.addWidget(self.operacion_label)

        input_layout = QHBoxLayout()
        self.layout.addLayout(input_layout)

        self.vector_a_label = QLabel("Vector A (x, y, z):")
        self.vector_a_input = QLineEdit()
        self.vector_a_input.setPlaceholderText("Ejemplo: (1, 2, 3)")

        self.vector_b_label = QLabel("Vector B (x, y, z):")
        self.vector_b_input = QLineEdit()
        self.vector_b_input.setPlaceholderText("Ejemplo: (4, 5, 6)")

        input_layout.addWidget(self.vector_a_label)
        input_layout.addWidget(self.vector_a_input)
        input_layout.addWidget(self.vector_b_label)
        input_layout.addWidget(self.vector_b_input)

        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.layout.addWidget(self.resultado)

        botones_layout = QGridLayout()
        self.layout.addLayout(botones_layout)

        operaciones = [
            ("Sumar", self.sumar_vectores),
            ("Restar", self.restar_vectores),
            ("Producto Punto", self.producto_punto),
            ("Producto Cruzado", self.producto_cruzado),
            ("Magnitud de A", self.magnitud),
        ]

        row, col = 0, 0
        for texto, funcion in operaciones:
            boton = QPushButton(texto)
            boton.clicked.connect(funcion)
            botones_layout.addWidget(boton, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        self.salir_button = QPushButton("Salir")
        self.salir_button.setObjectName("salir_button")
        self.salir_button.clicked.connect(self.salir)
        botones_layout.addWidget(self.salir_button, row, col)

    def validar_entrada(self, texto):
        try:
            texto = texto.strip("()")
            lista = [float(coord.strip()) for coord in texto.split(",")]
            if len(lista) == 3:
                return lista
            else:
                return None
        except ValueError:
            return None

    def sumar_vectores(self):
        a = self.vector_a_input.text()
        b = self.vector_b_input.text()

        a = self.validar_entrada(a)
        b = self.validar_entrada(b)

        if a and b:
            resultado = [a[i] + b[i] for i in range(3)]
            self.resultado.setText(self.formatear_resultado(f"Suma de A y B: {tuple(resultado)}"))
        else:
            self.resultado.setText("Error: Ingrese vectores válidos.")

    def restar_vectores(self):
        a = self.vector_a_input.text()
        b = self.vector_b_input.text()

        a = self.validar_entrada(a)
        b = self.validar_entrada(b)

        if a and b:
            resultado = [a[i] - b[i] for i in range(3)]
            self.resultado.setText(self.formatear_resultado(f"Resta de A y B: {tuple(resultado)}"))
        else:
            self.resultado.setText("Error: Ingrese vectores válidos.")

    def producto_punto(self):
        a = self.vector_a_input.text()
        b = self.vector_b_input.text()

        a = self.validar_entrada(a)
        b = self.validar_entrada(b)

        if a and b:
            resultado = sum([a[i] * b[i] for i in range(3)])
            self.resultado.setText(self.formatear_resultado(f"Producto punto de A y B: {resultado}"))
        else:
            self.resultado.setText("Error: Ingrese vectores válidos.")

    def producto_cruzado(self):
        a = self.vector_a_input.text()
        b = self.vector_b_input.text()

        a = self.validar_entrada(a)
        b = self.validar_entrada(b)

        if a and b:
            resultado = [
                a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0],
            ]
            self.resultado.setText(self.formatear_resultado(f"Producto cruzado de A y B: {tuple(resultado)}"))
        else:
            self.resultado.setText("Error: Ingrese vectores válidos.")

    def magnitud(self):
        a = self.vector_a_input.text()
        a = self.validar_entrada(a)

        if a:
            x, y, z = a
            magnitud_expr = sqrt(x**2 + y**2 + z**2)
            magnitud_valor = magnitud_expr.evalf()

            # Formato de número: eliminar .0 si es entero
            def format_number(n):
                return int(n) if float(n).is_integer() else round(float(n), 4)

            mag_format = format_number(magnitud_valor)

            # Construir el resultado con formato HTML
            resultado_html = (
                f"<b>Magnitud de A</b><br>"
                f"<b>Expresión simbólica:</b><br>"
                f"<pre>{pretty(magnitud_expr)}</pre><br>"
                f"<b>Valor numérico:</b> {mag_format}"
            )
            self.resultado.setHtml(resultado_html)
        else:
            self.resultado.setText("Error: Ingrese un vector válido.")

    def formatear_resultado(self, resultado):
        # Usar formato HTML para mejorar presentación general
        return f"<b>{resultado}</b>"

    def salir(self):
        from neuromate import MenuPrincipal
        self.menu = MenuPrincipal()
        self.menu.show()
        self.close()
