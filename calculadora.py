import sys
import numpy as np
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QSpinBox, QTextEdit, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QMessageBox, QGridLayout, QLineEdit,
    QSizePolicy, QGroupBox, QStyledItemDelegate
)
from PyQt5.QtGui import QIcon, QRegExpValidator, QDoubleValidator
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp


# Creamos un delegado personalizado para validar las entradas
class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        # Validador que permite números, punto decimal y signo negativo
        validator = QRegExpValidator(QRegExp(r"^[-]?[0-9]*\.?[0-9]*$"), editor)
        editor.setValidator(validator)
        return editor

    def setModelData(self, editor, model, index):
        text = editor.text().strip()
        
        # Si está vacío, usamos "0"
        if not text:
            text = "0"
        
        # Validamos que sea un número válido
        try:
            float(text)
            model.setData(index, text, Qt.EditRole)
        except ValueError:
            model.setData(index, "0", Qt.EditRole)


class MatrixCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧮 Calculadora Visual de Matrices")
        self.setGeometry(100, 100, 950, 650)
        self.setWindowIcon(QIcon("img/icon.png"))

        self.setStyleSheet("""
QWidget {
    background-color: #f9f9f9;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QLabel {
    font-weight: bold;
    padding: 2px 4px;
}

QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 2px solid #e53935;  /* rojo */
    padding: 4px;
    border-radius: 4px;
    min-width: 50px;
}

QComboBox {
    min-width: 100px;
}

QPushButton {
    background-color: #003366;  /* azul marino */
    color: white;
    border: none;
    padding: 6px 12px;
    margin: 2px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #002244;  /* más oscuro al pasar el mouse */
}

QPushButton#btn_exit {
    background-color: #e74c3c;
}

QPushButton#btn_exit:hover {
    background-color: #c0392b;
}

QTextEdit {
    background-color: #ffffff;
    border: 2px solid #e53935;  /* rojo */
    padding: 6px;
    border-radius: 4px;
    color: #2c3e50;
    min-height: 100px;
    font-size: 14px;
    font-family: 'Courier New', monospace;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ccc;
    border-radius: 4px;
    gridline-color: #d0d0d0;
}

QTableWidget::item {
    padding: 2px;
    text-align: center;
}

QHeaderView::section {
    background-color: #e0e0e0;
    color: #333;
    border: none;
    padding: 4px;
    font-weight: bold;
}

QLineEdit {
    border: 1px solid #bbb;
    border-radius: 3px;
    padding: 2px 4px;
    background: white;
}

QGroupBox {
    border: 1px solid #bbb;
    border-radius: 5px;
    margin-top: 10px;
    font-weight: bold;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}

QPushButton.matrix-fill-btn {
    background-color: #4CAF50;  /* verde */
    font-size: 12px;
    padding: 4px 8px;
}

QPushButton.matrix-fill-btn:hover {
    background-color: #388E3C;  /* verde oscuro */
}
""")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Panel de control
        control_panel = QGroupBox("Configuración de Matrices")
        control_layout = QGridLayout()
        control_panel.setLayout(control_layout)
        
        # Primera fila: Dimensiones Matriz A
        control_layout.addWidget(QLabel("Matriz A:"), 0, 0)
        control_layout.addWidget(QLabel("Filas:"), 0, 1)
        self.rows1 = QSpinBox()
        self.rows1.setRange(1, 10)
        self.rows1.setValue(2)
        control_layout.addWidget(self.rows1, 0, 2)
        
        control_layout.addWidget(QLabel("Columnas:"), 0, 3)
        self.cols1 = QSpinBox()
        self.cols1.setRange(1, 10)
        self.cols1.setValue(2)
        control_layout.addWidget(self.cols1, 0, 4)
        
        # Segunda fila: Dimensiones Matriz B
        control_layout.addWidget(QLabel("Matriz B:"), 1, 0)
        control_layout.addWidget(QLabel("Filas:"), 1, 1)
        self.rows2 = QSpinBox()
        self.rows2.setRange(1, 10)
        self.rows2.setValue(2)
        control_layout.addWidget(self.rows2, 1, 2)
        
        control_layout.addWidget(QLabel("Columnas:"), 1, 3)
        self.cols2 = QSpinBox()
        self.cols2.setRange(1, 10)
        self.cols2.setValue(2)
        control_layout.addWidget(self.cols2, 1, 4)
        
        # Orden de operación
        control_layout.addWidget(QLabel("Orden:"), 0, 5)
        self.combo_orden = QComboBox()
        self.combo_orden.addItems(["A ⭢ B", "B ⭢ A"])
        self.combo_orden.currentIndexChanged.connect(self.cambiar_orden)
        control_layout.addWidget(self.combo_orden, 0, 6)
        
        # Botones
        btn_panel = QHBoxLayout()
        self.btn_gen = QPushButton("Generar")
        self.btn_gen.clicked.connect(self.generar_tablas)
        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.clicked.connect(self.limpiar)
        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setObjectName("btn_exit")
        self.btn_exit.clicked.connect(self.salir)
        
        for btn in [self.btn_gen, self.btn_clear, self.btn_exit]:
            btn_panel.addWidget(btn)
        
        control_layout.addLayout(btn_panel, 1, 5, 1, 2)
        
        layout.addWidget(control_panel)

        # Contenedor para las matrices
        matrices_container = QHBoxLayout()
        layout.addLayout(matrices_container)
        
        # Matriz A con generador de matrices
        matriz_a_group = QGroupBox("Matriz A")
        matriz_a_layout = QVBoxLayout()
        
        # Añadir selector y botón para matriz A
        matrix_a_fill_layout = QHBoxLayout()
        self.combo_matriz_a = QComboBox()
        self.combo_matriz_a.addItems([
            "Seleccionar tipo...", "Aleatoria", "Simétrica", "Diagonal", 
            "Triangular Sup", "Triangular Inf", "Identidad", "Ceros", "Unos"
        ])
        matrix_a_fill_layout.addWidget(self.combo_matriz_a)
        
        self.btn_fill_a = QPushButton("Rellenar")
        self.btn_fill_a.setProperty("class", "matrix-fill-btn")
        self.btn_fill_a.clicked.connect(lambda: self.fill_special_matrix("A"))
        matrix_a_fill_layout.addWidget(self.btn_fill_a)
        
        matriz_a_layout.addLayout(matrix_a_fill_layout)
        
        # Layout para la tabla A
        self.matrices_layout_a = QVBoxLayout()
        matriz_a_layout.addLayout(self.matrices_layout_a)
        matriz_a_group.setLayout(matriz_a_layout)
        matrices_container.addWidget(matriz_a_group)
        
        # Matriz B con generador de matrices
        matriz_b_group = QGroupBox("Matriz B")
        matriz_b_layout = QVBoxLayout()
        
        # Añadir selector y botón para matriz B
        matrix_b_fill_layout = QHBoxLayout()
        self.combo_matriz_b = QComboBox()
        self.combo_matriz_b.addItems([
            "Seleccionar tipo...", "Aleatoria", "Simétrica", "Diagonal", 
            "Triangular Sup", "Triangular Inf", "Identidad", "Ceros", "Unos"
        ])
        matrix_b_fill_layout.addWidget(self.combo_matriz_b)
        
        self.btn_fill_b = QPushButton("Rellenar")
        self.btn_fill_b.setProperty("class", "matrix-fill-btn")
        self.btn_fill_b.clicked.connect(lambda: self.fill_special_matrix("B"))
        matrix_b_fill_layout.addWidget(self.btn_fill_b)
        
        matriz_b_layout.addLayout(matrix_b_fill_layout)
        
        # Layout para la tabla B
        self.matrices_layout_b = QVBoxLayout()
        matriz_b_layout.addLayout(self.matrices_layout_b)
        matriz_b_group.setLayout(matriz_b_layout)
        matrices_container.addWidget(matriz_b_group)
        
        # Operaciones
        operations_panel = QGroupBox("Operaciones")
        operations_layout = QHBoxLayout()
        operations_panel.setLayout(operations_layout)
        
        self.agregar_boton("Sumar", self.sumar, operations_layout)
        self.agregar_boton("Restar", self.restar, operations_layout)
        self.agregar_boton("Multiplicar", self.multiplicar, operations_layout)
        self.agregar_boton("Determinante", self.determinantes, operations_layout)
        self.agregar_boton("Inversas", self.inversas, operations_layout)
        self.agregar_boton("Sistemas Lineales", self.abrir_sistemas_lineales, operations_layout)
        
        layout.addWidget(operations_panel)
        
        # Resultados
        results_panel = QGroupBox("Resultado")
        results_layout = QVBoxLayout()
        results_panel.setLayout(results_layout)
        
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        results_layout.addWidget(self.resultado)
        
        layout.addWidget(results_panel)

        # Crear delegado numérico para validación
        self.numeric_delegate = NumericDelegate()

        self.generar_tablas()

    def agregar_boton(self, texto, funcion, layout):
        btn = QPushButton(texto)
        btn.clicked.connect(funcion)
        layout.addWidget(btn)

    def generar_tablas(self):
        # Limpiamos los layouts anteriores
        self.limpiar_layout(self.matrices_layout_a)
        self.limpiar_layout(self.matrices_layout_b)
        
        # Creamos las nuevas tablas con tamaños compactos
        self.tabla1 = self.crear_tabla_compacta(self.rows1.value(), self.cols1.value())
        self.tabla2 = self.crear_tabla_compacta(self.rows2.value(), self.cols2.value())
        
        # Agregamos a los layouts
        self.matrices_layout_a.addWidget(self.tabla1)
        self.matrices_layout_b.addWidget(self.tabla2)

    def crear_tabla_compacta(self, filas, columnas):
        tabla = QTableWidget(filas, columnas)
        tabla.horizontalHeader().setDefaultSectionSize(40)
        tabla.verticalHeader().setDefaultSectionSize(30)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        tabla.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Configuramos el delegado para validación numérica
        tabla.setItemDelegate(self.numeric_delegate)
        
        # Añadimos valores iniciales a cada celda
        for i in range(filas):
            for j in range(columnas):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(i, j, item)
        
        return tabla
    
    def limpiar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def validar_entrada(self, texto):
        """Valida que el texto ingresado sea un número válido"""
        if not texto:
            return 0.0
        try:
            # Permite notación científica y decimales
            return float(texto)
        except ValueError:
            return None
            
    def fill_special_matrix(self, matriz_id):
        """Rellena la matriz seleccionada con un tipo especial de matriz"""
        # Determinar qué matriz y combo box usar
        if matriz_id == "A":
            tabla = self.tabla1
            combo = self.combo_matriz_a
            filas = self.rows1.value()
            columnas = self.cols1.value()
        else:  # matriz_id == "B"
            tabla = self.tabla2
            combo = self.combo_matriz_b
            filas = self.rows2.value()
            columnas = self.cols2.value()
            
        matrix_type = combo.currentText()
        if matrix_type == "Seleccionar tipo...":
            return
            
        # Crear matriz según el tipo seleccionado
        matrix = np.zeros((filas, columnas))
        
        # Verificar si necesitamos una matriz cuadrada para ciertos tipos
        need_square = matrix_type in ["Simétrica", "Diagonal", "Triangular Sup", "Triangular Inf", "Identidad"]
        
        if need_square and filas != columnas:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                f"El tipo '{matrix_type}' requiere una matriz cuadrada.\nPor favor, ajuste las dimensiones."
            )
            combo.setCurrentIndex(0)  # Resetear a "Seleccionar tipo..."
            return
            
        # Generar según el tipo
        if matrix_type == "Aleatoria":
            matrix = np.random.randint(-10, 11, (filas, columnas))
            
        elif matrix_type == "Simétrica":
            temp = np.random.randint(-10, 11, (filas, columnas))
            matrix = (temp + temp.T) // 2
            
        elif matrix_type == "Diagonal":
            for i in range(filas):
                matrix[i, i] = np.random.randint(-10, 11)
                
        elif matrix_type == "Triangular Sup":
            for i in range(filas):
                for j in range(i, columnas):
                    matrix[i, j] = np.random.randint(-10, 11)
                    
        elif matrix_type == "Triangular Inf":
            for i in range(filas):
                for j in range(min(i + 1, columnas)):
                    matrix[i, j] = np.random.randint(-10, 11)
                    
        elif matrix_type == "Identidad":
            matrix = np.eye(min(filas, columnas))
            
        elif matrix_type == "Ceros":
            matrix = np.zeros((filas, columnas))
            
        elif matrix_type == "Unos":
            matrix = np.ones((filas, columnas))
            
        # Llenar la tabla con los valores generados
        for i in range(filas):
            for j in range(columnas):
                item = QTableWidgetItem(str(int(matrix[i, j])))
                item.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(i, j, item)
                
        # Resetear el combo box
        combo.setCurrentIndex(0)

    def leer_matriz(self, tabla):
        filas = tabla.rowCount()
        columnas = tabla.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                item = tabla.item(i, j)
                valor = self.validar_entrada(item.text() if item else "0")
                if valor is None:
                    raise ValueError(f"Error en la celda ({i+1}, {j+1}): Valor no válido.")
                fila.append(valor)
                # Actualiza el valor en la celda para mostrar formato correcto
                tabla.setItem(i, j, QTableWidgetItem(str(valor)))
            matriz.append(fila)
        return np.array(matriz)

    def mostrar_error(self, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error en la Operación")
        msg.setText(mensaje)
        msg.setInformativeText("Por favor, revisa los datos ingresados.")
        msg.exec_()

    def obtener_ordenadas(self):
        orden = self.combo_orden.currentText()
        try:
            a = self.leer_matriz(self.tabla1)
            b = self.leer_matriz(self.tabla2)
            return (a, b) if orden == "A ⭢ B" else (b, a)
        except ValueError as e:
            self.mostrar_error(str(e))
            raise

    def format_result(self, resultado):
        if isinstance(resultado, np.ndarray):
            return f"<pre>{np.array2string(resultado, precision=2, suppress_small=True)}</pre>"
        elif isinstance(resultado, float):
            return str(int(resultado)) if resultado.is_integer() else str(round(resultado, 2))
        return str(resultado)

    def mostrar_resultado(self, resultado, titulo="Resultado"):
        html = f"<b>{titulo}:</b><br>{self.format_result(resultado)}"
        self.resultado.setHtml(html)

    def sumar(self):
        try:
            a, b = self.obtener_ordenadas()
            if a.shape != b.shape:
                raise ValueError("Las matrices deben tener las mismas dimensiones para sumar.")
            res = a + b
            self.mostrar_resultado(res, "Suma")
        except Exception as e:
            self.mostrar_error(str(e))

    def restar(self):
        try:
            a, b = self.obtener_ordenadas()
            if a.shape != b.shape:
                raise ValueError("Las matrices deben tener las mismas dimensiones para restar.")
            res = a - b
            self.mostrar_resultado(res, "Resta")
        except Exception as e:
            self.mostrar_error(str(e))

    def multiplicar(self):
        try:
            a, b = self.obtener_ordenadas()
            if a.shape[1] != b.shape[0]:
                raise ValueError("Columnas de la primera deben coincidir con filas de la segunda.")
            res = np.dot(a, b)
            self.mostrar_resultado(res, "Multiplicación")
        except Exception as e:
            self.mostrar_error(str(e))

    def determinantes(self):
        try:
            a = self.leer_matriz(self.tabla1)
            b = self.leer_matriz(self.tabla2)
            resultados = []
            
            # Determinante A
            if a.shape[0] == a.shape[1]:
                det_a = round(np.linalg.det(a), 2)
                resultados.append(f"<b>Determinante A:</b> {self.format_result(det_a)}")
            else:
                resultados.append("<b>Matriz A no es cuadrada.</b>")
                
            # Determinante B
            if b.shape[0] == b.shape[1]:
                det_b = round(np.linalg.det(b), 2)
                resultados.append(f"<b>Determinante B:</b> {self.format_result(det_b)}")
            else:
                resultados.append("<b>Matriz B no es cuadrada.</b>")
                
            self.resultado.setHtml("<br><br>".join(resultados))
        except Exception as e:
            self.mostrar_error(str(e))

    def inversas(self):
        mensajes = []
        try:
            a = self.leer_matriz(self.tabla1)
            if a.shape[0] == a.shape[1]:
                det_a = np.linalg.det(a)
                if abs(det_a) < 1e-10:  # Mejor comprobación para matrices singulares
                    mensajes.append("<b>Matriz A es singular o casi singular.</b>")
                else:
                    inv_a = np.linalg.inv(a)
                    mensajes.append(f"<b>Inversa A:</b><br>{self.format_result(inv_a)}")
            else:
                mensajes.append("<b>Matriz A no es cuadrada.</b>")
        except np.linalg.LinAlgError:
            mensajes.append("<b>Error al calcular inversa de A.</b>")
        except Exception as e:
            mensajes.append(f"<b>Error A:</b> {str(e)}")

        try:
            b = self.leer_matriz(self.tabla2)
            if b.shape[0] == b.shape[1]:
                det_b = np.linalg.det(b)
                if abs(det_b) < 1e-10:
                    mensajes.append("<b>Matriz B es singular o casi singular.</b>")
                else:
                    inv_b = np.linalg.inv(b)
                    mensajes.append(f"<b>Inversa B:</b><br>{self.format_result(inv_b)}")
            else:
                mensajes.append("<b>Matriz B no es cuadrada.</b>")
        except np.linalg.LinAlgError:
            mensajes.append("<b>Error al calcular inversa de B.</b>")
        except Exception as e:
            mensajes.append(f"<b>Error B:</b> {str(e)}")

        self.resultado.setHtml("<br><br>".join(mensajes))

    def limpiar(self):
        self.resultado.clear()
        self.generar_tablas()

    def cambiar_orden(self):
        self.resultado.clear()

    def abrir_sistemas_lineales(self):
        self.sistema = SistemasLineales()
        self.sistema.show()
        self.hide()

    def salir(self):
        from neuromate import MenuPrincipal
        self.menu = MenuPrincipal()
        self.menu.show()
        self.close()

class SistemasLineales(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resolver sistema de ecuaciones lineales")
        self.setGeometry(100, 100, 800, 600)
        
        self.setStyleSheet("""
QWidget {
    background-color: #f9f9f9;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QLabel {
    font-weight: bold;
    padding: 4px 6px;
}

QPushButton {
    background-color: #003366;
    color: white;
    border: none;
    padding: 8px 16px;
    margin: 4px;
    border-radius: 6px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #002244;
}

QPushButton#btn_exit {
    background-color: #e74c3c;
}

QPushButton#btn_exit:hover {
    background-color: #c0392b;
}

QTextEdit {
    background-color: #ffffff;
    border: 2px solid #e53935;
    padding: 10px;
    border-radius: 8px;
    color: #2c3e50;
    min-height: 120px;
    font-size: 15px;
    font-family: 'Courier New', monospace;
}

QGroupBox {
    border: 1px solid #bbb;
    border-radius: 5px;
    margin-top: 10px;
    font-weight: bold;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
""")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Grupo para las instrucciones y entrada
        input_group = QGroupBox("Sistema de Ecuaciones")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        
        self.instrucciones = QLabel("Escribe un sistema de ecuaciones lineales (una por línea):")
        input_layout.addWidget(self.instrucciones)

        self.editor_ecuaciones = QTextEdit()
        self.editor_ecuaciones.setPlaceholderText(
            "Ejemplo:\nx - 3y + 2z = -3\n5x + 6y - z = 13\n4x - y + 3z = 8"
        )
        input_layout.addWidget(self.editor_ecuaciones)
        
        layout.addWidget(input_group)

        # Grupo para los botones de acción
        action_layout = QHBoxLayout()
        
        self.boton_resolver = QPushButton("Resolver sistema")
        self.boton_resolver.clicked.connect(self.resolver)
        action_layout.addWidget(self.boton_resolver)
        
        self.boton_limpiar = QPushButton("Limpiar")
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        action_layout.addWidget(self.boton_limpiar)
        
        layout.addLayout(action_layout)

        # Grupo para los resultados
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        result_group.setLayout(result_layout)
        
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        result_layout.addWidget(self.resultado)
        
        layout.addWidget(result_group)

        # Botón para volver
        volver_layout = QHBoxLayout()
        self.boton_volver = QPushButton("Volver a Calculadora")
        self.boton_volver.clicked.connect(self.volver_a_calculadora)
        self.boton_volver.setObjectName("btn_exit")
        volver_layout.addStretch()
        volver_layout.addWidget(self.boton_volver)
        volver_layout.addStretch()
        layout.addLayout(volver_layout)

    def limpiar_campos(self):
        self.editor_ecuaciones.clear()
        self.resultado.clear()
        
    def volver_a_calculadora(self):
        from neuromate import MenuMatrices
        self.calc = MenuMatrices()
        self.calc.show()
        self.close()

    def analizar_sistema(self, texto):
        """Analiza el sistema de ecuaciones y extrae los coeficientes y términos independientes"""
        lineas = texto.strip().split('\n')
        # Identificar todas las variables únicas en el sistema
        variables = sorted(list(set(re.findall(r'[a-zA-Z]', texto))))
        
        A = []  # Matriz de coeficientes
        B = []  # Vector de términos independientes
        
        for linea in lineas:
            if '=' not in linea:
                raise ValueError(f"La ecuación '{linea}' no contiene el símbolo =")
                
            coeficientes = [0] * len(variables)
            try:
                izquierda, derecha = linea.split('=')
                
                # Procesar lado izquierdo (términos con variables)
                izquierda = izquierda.replace(' ', '')
                terminos = re.findall(r'[\+\-]?\d*\.?\d*[a-zA-Z]', izquierda)
                
                for termino in terminos:
                    match = re.match(r'([\+\-]?\d*\.?\d*)([a-zA-Z])', termino)
                    if match:
                        coef_str, var = match.groups()
                        # Manejar coeficientes implícitos (x = 1x, -x = -1x)
                        if coef_str in ['', '+', '-']:
                            coef_str += '1'
                        coef = float(coef_str)
                        
                        # Buscar el índice de la variable
                        try:
                            idx = variables.index(var)
                            coeficientes[idx] = coef
                        except ValueError:
                            raise ValueError(f"Variable '{var}' no encontrada en el sistema")
                
                # Procesar lado derecho (término independiente)
                try:
                    termino_independiente = float(derecha.strip())
                    B.append(termino_independiente)
                except ValueError:
                    raise ValueError(f"El término independiente '{derecha.strip()}' no es un número válido")
                
                A.append(coeficientes)
                
            except Exception as e:
                raise ValueError(f"Error en la ecuación '{linea}': {str(e)}")
        
        # Verificar que la matriz y el vector sean del mismo tamaño
        if len(A) != len(B):
            raise ValueError("Número de ecuaciones no coincide con número de términos independientes")
            
        return np.array(A), np.array(B), variables

    def resolver_sistema(self, A, B):
        """Resuelve el sistema de ecuaciones lineales Ax = B"""
        try:
            # Verificar si el sistema tiene solución única
            if A.shape[0] != A.shape[1]:
                if A.shape[0] < A.shape[1]:
                    return "El sistema tiene infinitas soluciones (más variables que ecuaciones)"
                else:
                    return "El sistema está sobredeterminado (más ecuaciones que variables)"
                    
            # Verificar si la matriz es singular (determinante cerca de cero)
            det = np.linalg.det(A)
            if abs(det) < 1e-10:
                return "El sistema no tiene solución única (matriz singular)"
                
            # Resolver el sistema
            x = np.linalg.solve(A, B)
            return x
        except np.linalg.LinAlgError as e:
            return f"Error al resolver el sistema: {e}"
        except Exception as e:
            return f"Error inesperado: {e}"

    def resolver(self):
        """Resuelve el sistema de ecuaciones lineales ingresado por el usuario"""
        texto = self.editor_ecuaciones.toPlainText()
        if not texto.strip():
            QMessageBox.warning(self, "Advertencia", "Por favor escribe un sistema de ecuaciones.")
            return

        try:
            # Analizar el sistema
            A, B, variables = self.analizar_sistema(texto)
            
            # Mostrar la matriz y el vector
            matriz_info = (
                f"<b>Variables:</b> {', '.join(variables)}<br>"
                f"<b>Matriz de Coeficientes:</b><br>"
                f"<pre>{np.array2string(A, precision=2)}</pre><br>"
                f"<b>Vector de Términos Independientes:</b><br>"
                f"<pre>{np.array2string(B, precision=2)}</pre><br>"
            )
            
            # Resolver el sistema
            resultado = self.resolver_sistema(A, B)
            
            if isinstance(resultado, str):
                # Si es un mensaje de error o advertencia
                self.resultado.setHtml(f"{matriz_info}<br><b>Resultado:</b> {resultado}")
            else:
                # Si es la solución (vector)
                texto_resultado = "<br>".join(
                    f"<b>{var} = {round(valor, 4)}</b>" for var, valor in zip(variables, resultado)
                )
                self.resultado.setHtml(f"{matriz_info}<br><b>Solución:</b><br>{texto_resultado}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al analizar el sistema:\n{str(e)}")