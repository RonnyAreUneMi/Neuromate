import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QFrame, QGroupBox, QHeaderView,
    QComboBox, QRadioButton, QButtonGroup, QSplitter, QFormLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')
plt.style.use('seaborn-v0_8-whitegrid')


class vyvpropios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cálculo de Valores y Vectores Propios")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #F6F1F1;
                color: #333333;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLabel {
                color: #333333;
                font-weight: normal;
            }
            QLabel.title {
                color: #19A7CE;
                font-weight: bold;
                font-size: 20px;
            }
            QLabel.subtitle {
                color: #19A7CE;
                font-weight: bold;
            }
            QLabel.info {
                color: #333333;
                font-weight: normal;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 4px;
                padding: 4px;
                color: #333333;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #19A7CE;
            }
            QPushButton {
                background-color: #19A7CE;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #146C94;
            }
            QPushButton:pressed {
                background-color: #146C94;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                gridline-color: #AEFEFF;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #E3F4F9;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #19A7CE;
                color: white;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #19A7CE;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #19A7CE;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 4px;
                padding: 4px;
                min-height: 22px;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QRadioButton::indicator:checked {
                background-color: #19A7CE;
                border: 2px solid #19A7CE;
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
                border: 2px solid #19A7CE;
                border-radius: 7px;
            }
            QSplitter::handle {
                background-color: #19A7CE;
                width: 2px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Título
        title_layout = QHBoxLayout()
        title = QLabel("Cálculo de Valores y Vectores Propios")
        title.setProperty("class", "title")
        title_layout.addWidget(title)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Contenedor principal con splitter para mejor distribución
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Entrada de matriz
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Parámetros de entrada
        input_group = QGroupBox("Configuración de Matriz")
        input_layout = QFormLayout()

        # Fila superior: Tamaño y tipo de matriz
        top_controls = QHBoxLayout()
        
        # Selección de tamaño de matriz
        matrix_size_label = QLabel("Dimensión:")
        matrix_size_label.setProperty("class", "subtitle")
        matrix_size_label.setMaximumWidth(70)
        self.matrix_size_input = QSpinBox()
        self.matrix_size_input.setRange(2, 3)  # Limitado a 2x2 o 3x3
        self.matrix_size_input.setValue(2)
        self.matrix_size_input.setMaximumWidth(50)
        self.matrix_size_input.valueChanged.connect(self.update_matrix_input)
        self.matrix_size_input.valueChanged.connect(self.update_vector_inputs)
        
        top_controls.addWidget(matrix_size_label)
        top_controls.addWidget(self.matrix_size_input)
        
        # Tipo de matriz
        self.special_type = QComboBox()
        self.special_type.addItems(["Manual", "Aleatoria", "Simétrica", "Diagonal", "Triangular Sup", "Triangular Inf", "Identidad"])
        self.special_type.currentIndexChanged.connect(self.change_matrix_type)
        self.special_type.setMaximumWidth(120)
        
        matrix_type_label = QLabel("Tipo:")
        matrix_type_label.setProperty("class", "subtitle")
        matrix_type_label.setMaximumWidth(40)
        top_controls.addWidget(matrix_type_label)
        top_controls.addWidget(self.special_type)
        
        top_controls.addStretch()
        
        # Botón calcular (integrado en la fila superior)
        self.calc_btn = QPushButton("Calcular")
        self.calc_btn.setMinimumWidth(80)
        self.calc_btn.clicked.connect(self.calcular)
        top_controls.addWidget(self.calc_btn)
        
        # Añadir la fila superior al layout input (forma horizontal + form layout complicaría, agregamos en vertical)
        top_controls_container = QVBoxLayout()
        top_controls_container.addLayout(top_controls)
        input_layout.addRow(top_controls_container)

        # Tabla para entrada de matriz
        self.matrix_table = QTableWidget()
        self.matrix_table.setAlternatingRowColors(True)
        self.matrix_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #F0F8FF;
            }
            QTableWidget::item {
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        input_layout.addRow(self.matrix_table)
        
        # Inicializar tabla
        self.update_matrix_input()
        
        # Grupo para entrada de vectores de prueba
        vector_group = QGroupBox("Vector de Entrada")
        vector_layout = QFormLayout()
        
        # Crear campos para x, y, z
        self.vector_inputs = {}
        for coord in ['x', 'y', 'z']:
            self.vector_inputs[coord] = QDoubleSpinBox()
            self.vector_inputs[coord].setRange(-100, 100)
            self.vector_inputs[coord].setValue(1.0)
            self.vector_inputs[coord].setSingleStep(0.5)
            self.vector_inputs[coord].setDecimals(2)
            vector_layout.addRow(f"Valor de {coord}:", self.vector_inputs[coord])
        
        # Inicialmente mostrar solo x e y
        self.update_vector_inputs()
        
        vector_group.setLayout(vector_layout)
        input_layout.addRow(vector_group)

        # Input paso h
        self.h_input = QDoubleSpinBox()
        self.h_input.setRange(0.01, 10.0)
        self.h_input.setValue(0.1)
        self.h_input.setDecimals(2)
        self.h_input.setSingleStep(0.01)
        h_label = QLabel("Paso h:")
        h_label.setProperty("class", "subtitle")
        input_layout.addRow(h_label, self.h_input)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group, 1)  # Añadir factor de estiramiento
        
        # Panel derecho: Resultados
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        
        # Tabla combinada de valores y vectores propios
        self.eigens_table = QTableWidget()
        self.eigens_table.setAlternatingRowColors(True)
        self.eigens_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #F0F8FF;
            }
            QTableWidget::item {
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        results_layout.addWidget(self.eigens_table)
        
        # Información adicional
        info_frame = QFrame()
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Determinante y diagonalizable
        det_diag_layout = QVBoxLayout()
        self.det_label = QLabel("Determinante: ")
        self.det_label.setProperty("class", "info")
        self.rank_label = QLabel("Rango: ")
        self.rank_label.setProperty("class", "info")
        self.diag_label = QLabel("Diagonalizable: ")
        self.diag_label.setProperty("class", "info")
        
        # Resultado de la transformación
        self.transform_label = QLabel("Vector transformado: ")
        self.transform_label.setProperty("class", "info")
        
        det_diag_layout.addWidget(self.det_label)
        det_diag_layout.addWidget(self.rank_label)
        det_diag_layout.addWidget(self.diag_label)
        det_diag_layout.addWidget(self.transform_label)
        info_layout.addLayout(det_diag_layout)
        info_layout.addStretch()
        
        results_layout.addWidget(info_frame)
        
        # Gráfica para visualización
        self.figure = plt.figure(figsize=(5, 4), dpi=80)
        self.figure.patch.set_facecolor('#F6F1F1')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(200)
        self.ax = None  # Inicializamos ax como None para crearlo según necesitemos
        
        results_layout.addWidget(self.canvas, 1)  # Añadir factor de estiramiento
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group, 1)  # Añadir factor de estiramiento
        
        # Añadir paneles al splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([350, 550])  # Proporciones iniciales
        
        main_layout.addWidget(main_splitter, 1)  # Añadir factor de estiramiento para responsividad
        self.setLayout(main_layout)

    def update_vector_inputs(self):
        size = self.matrix_size_input.value()
        # Mostrar u ocultar el campo z según la dimensión
        self.vector_inputs['z'].setVisible(size == 3)
        # Buscar la etiqueta que acompaña al campo z de manera segura
        parent = self.vector_inputs['z'].parentWidget()
        if parent and hasattr(parent, 'layout') and parent.layout():
            if hasattr(parent.layout(), 'labelForField'):
                label = parent.layout().labelForField(self.vector_inputs['z'])
                if label:
                    label.setVisible(size == 3)

    def update_matrix_input(self):
        size = self.matrix_size_input.value()
        self.matrix_table.setRowCount(size)
        self.matrix_table.setColumnCount(size)
        
        # Configurar encabezados
        headers = [str(i+1) for i in range(size)]
        self.matrix_table.setHorizontalHeaderLabels(headers)
        self.matrix_table.setVerticalHeaderLabels(headers)
        
        # Establecer valores por defecto
        for i in range(size):
            for j in range(size):
                if not self.matrix_table.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.matrix_table.setItem(i, j, item)
        
        # Ajustar tamaño
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Si no está en modo manual, actualizar los valores
        current_type = self.special_type.currentText()
        if current_type != "Manual":
            self.fill_special_matrix(current_type)

    def change_matrix_type(self):
        current_type = self.special_type.currentText()
        if current_type != "Manual":
            self.fill_special_matrix(current_type)
    
    def fill_special_matrix(self, matrix_type):
        size = self.matrix_size_input.value()
        matrix = np.zeros((size, size))
        
        if matrix_type == "Aleatoria":
            matrix = np.random.randint(-10, 11, (size, size))
            
        elif matrix_type == "Simétrica":
            temp = np.random.randint(-10, 11, (size, size))
            matrix = (temp + temp.T) // 2
            
        elif matrix_type == "Diagonal":
            for i in range(size):
                matrix[i, i] = np.random.randint(-10, 11)
                
        elif matrix_type == "Triangular Sup":
            for i in range(size):
                for j in range(i, size):
                    matrix[i, j] = np.random.randint(-10, 11)
                    
        elif matrix_type == "Triangular Inf":
            for i in range(size):
                for j in range(i + 1):
                    matrix[i, j] = np.random.randint(-10, 11)
                    
        elif matrix_type == "Identidad":
            matrix = np.eye(size)
        
        # Llenar la tabla
        for i in range(size):
            for j in range(size):
                item = QTableWidgetItem(str(int(matrix[i, j])))
                item.setTextAlignment(Qt.AlignCenter)
                self.matrix_table.setItem(i, j, item)

    def get_matrix_from_table(self):
        size = self.matrix_size_input.value()
        matrix = np.zeros((size, size))
        
        for i in range(size):
            for j in range(size):
                try:
                    value = float(self.matrix_table.item(i, j).text())
                    matrix[i, j] = value
                except (ValueError, AttributeError):
                    QMessageBox.warning(self, "Error de Entrada", 
                                    f"Valor inválido en la posición ({i+1},{j+1}). Usando 0.")
                    matrix[i, j] = 0
        
        return matrix

    def get_input_vector(self):
        size = self.matrix_size_input.value()
        vector = np.zeros(size)
        
        vector[0] = self.vector_inputs['x'].value()
        vector[1] = self.vector_inputs['y'].value()
        
        if size == 3:
            vector[2] = self.vector_inputs['z'].value()
        
        return vector

    def calcular(self):
        try:
            # Obtener la matriz desde la tabla
            matrix = self.get_matrix_from_table()
            
            # Obtener vector de entrada
            input_vector = self.get_input_vector()
            
            # Obtener el valor de h
            h = self.h_input.value()
            
            # Escalar el vector de entrada por h
            scaled_vector = input_vector * h
            
            # Calcular la transformación del vector escalado
            transformed_vector = np.dot(matrix, scaled_vector)
            
            # Mostrar el resultado de la transformación
            if self.matrix_size_input.value() == 2:
                self.transform_label.setText(f"Vector transformado: ({transformed_vector[0]:.2f}, {transformed_vector[1]:.2f})")
            else:
                self.transform_label.setText(f"Vector transformado: ({transformed_vector[0]:.2f}, {transformed_vector[1]:.2f}, {transformed_vector[2]:.2f})")
            
            # Calcular valores y vectores propios
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            
            # Preparar tabla combinada
            size = self.matrix_size_input.value()
            self.eigens_table.clear()
            self.eigens_table.setRowCount(size)
            self.eigens_table.setColumnCount(size + 1)  # +1 para los valores propios
            
            # Configurar encabezados
            headers = ["Valor λ"] + [f"Vector v{i+1}" for i in range(size)]
            self.eigens_table.setHorizontalHeaderLabels(headers)
            row_headers = [f"Comp. {i+1}" for i in range(size)]
            self.eigens_table.setVerticalHeaderLabels(row_headers)
            
            # Llenar la tabla
            for j in range(size):
                # Valores propios (primera columna)
                lambda_val = eigenvalues[j]
                lambda_item = QTableWidgetItem(f"{lambda_val.real:.4f}")
                lambda_item.setTextAlignment(Qt.AlignCenter)
                # Colorear según magnitud del valor propio
                if abs(lambda_val.real) > 1:
                    lambda_item.setBackground(Qt.green)
                elif abs(lambda_val.real) < 1:
                    lambda_item.setBackground(Qt.yellow)
                self.eigens_table.setItem(j, 0, lambda_item)
                
                # Vectores propios (columnas restantes)
                for i in range(size):
                    val = eigenvectors[i, j]
                    # Solo mostramos la parte real
                    item = QTableWidgetItem(f"{val.real:.4f}")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.eigens_table.setItem(i, j + 1, item)
            
            # Ajustar tamaño de la tabla
            self.eigens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.eigens_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Información adicional
            det_val = np.linalg.det(matrix)
            rank_val = np.linalg.matrix_rank(matrix)
            
            # Verificar si es diagonalizable
            # Una matriz es diagonalizable si el número de vectores propios linealmente
            # independientes es igual a la dimensión de la matriz
            is_diagonalizable = len(np.unique(eigenvalues)) == len(eigenvalues)
            
            self.det_label.setText(f"Determinante: {det_val:.4f}")
            self.rank_label.setText(f"Rango: {rank_val}")
            self.diag_label.setText(f"Diagonalizable: {'Sí' if is_diagonalizable else 'No'}")
            
            # Limpiar la figura actual para asegurarnos de que no haya problemas al cambiar de dimensión
            self.figure.clear()
            
            # Visualización (solo para 2x2 o 3x3)
            if size == 2:
                # Para matrices 2x2, creamos un nuevo eje 2D
                self.ax = self.figure.add_subplot(111)
                self.ax.set_facecolor('#FFFFFF')
                
                # Para matrices 2x2, visualizar la transformación de un cuadrado unitario
                square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
                transformed = np.dot(square, matrix)
                
                # Dibujar cuadrado original
                self.ax.plot(square[:, 0], square[:, 1], 'b--', label='Original', linewidth=2)
                
                # Dibujar cuadrado transformado
                self.ax.plot(transformed[:, 0], transformed[:, 1], 'r-', label='Transformado', linewidth=2)
                
                # Dibujar vectores propios
                for i, vec in enumerate(eigenvectors.T):
                    vec_real = np.real(vec)
                    self.ax.arrow(0, 0, vec_real[0], vec_real[1], 
                                  head_width=0.05, head_length=0.1, 
                                  fc=f'C{i+2}', ec=f'C{i+2}', 
                                  label=f'λ{i+1}={eigenvalues[i].real:.2f}',
                                  linewidth=2)
                
                # Dibujar vector de entrada y su transformación
                self.ax.arrow(0, 0, scaled_vector[0], scaled_vector[1], 
                              head_width=0.05, head_length=0.1, 
                              fc='purple', ec='purple', 
                              label=f'Vector ({scaled_vector[0]:.1f},{scaled_vector[1]:.1f})',
                              linewidth=2)
                
                # Fase intermedia: primero movemos en x, luego en y
                self.ax.plot([0, scaled_vector[0]], [0, 0], 'g--', linewidth=1)
                self.ax.plot([scaled_vector[0], scaled_vector[0]], [0, scaled_vector[1]], 'g--', linewidth=1)
                
                # Dibujamos el vector transformado
                self.ax.arrow(0, 0, transformed_vector[0], transformed_vector[1], 
                              head_width=0.05, head_length=0.1, 
                              fc='orange', ec='orange', 
                              label=f'Transformado ({transformed_vector[0]:.1f},{transformed_vector[1]:.1f})',
                              linewidth=2)
                
                # Configuración adicional
                self.ax.grid(True)
                self.ax.legend(loc='best', fontsize=9)
                self.ax.set_aspect('equal')
                self.ax.set_xlabel('x')
                self.ax.set_ylabel('y')
                self.ax.set_title('Transformación 2D', fontsize=10)
                
            elif size == 3:
                # Para matrices 3x3, creamos un nuevo eje 3D
                self.ax = self.figure.add_subplot(111, projection='3d')
                
                # Dibujar los ejes
                self.ax.quiver(0, 0, 0, 1, 0, 0, color='r', label='X', linewidth=2)
                self.ax.quiver(0, 0, 0, 0, 1, 0, color='g', label='Y', linewidth=2)
                self.ax.quiver(0, 0, 0, 0, 0, 1, color='b', label='Z', linewidth=2)
                
                # Dibujar vectores propios
                for i, vec in enumerate(eigenvectors.T):
                    vec_real = np.real(vec)
                    self.ax.quiver(0, 0, 0, vec_real[0], vec_real[1], vec_real[2], 
                                  color=f'C{i+3}', 
                                  label=f'λ{i+1}={eigenvalues[i].real:.2f}',
                                  linewidth=2)
                
                # Dibujar vector de entrada
                self.ax.quiver(0, 0, 0, scaled_vector[0], scaled_vector[1], scaled_vector[2],
                              color='purple',
                              label=f'Vector ({scaled_vector[0]:.1f},{scaled_vector[1]:.1f},{scaled_vector[2]:.1f})',
                              linewidth=2)
                
                # Mostrar pasos intermedios con líneas punteadas
                self.ax.plot([0, scaled_vector[0]], [0, 0], [0, 0], 'g--', linewidth=1)
                self.ax.plot([scaled_vector[0], scaled_vector[0]], [0, scaled_vector[1]], [0, 0], 'g--', linewidth=1)
                self.ax.plot([scaled_vector[0], scaled_vector[0]], [scaled_vector[1], scaled_vector[1]], [0, scaled_vector[2]], 'g--', linewidth=1)
                
                # Dibujar vector transformado
                self.ax.quiver(0, 0, 0, transformed_vector[0], transformed_vector[1], transformed_vector[2],
                              color='orange',
                              label=f'Transformado ({transformed_vector[0]:.1f},{transformed_vector[1]:.1f},{transformed_vector[2]:.1f})',
                              linewidth=2)
                
                # Configuración adicional
                self.ax.set_xlabel('X')
                self.ax.set_ylabel('Y')
                self.ax.set_zlabel('Z')
                self.ax.set_title('Vectores Propios 3D', fontsize=10)
                self.ax.legend(loc='best', fontsize=9)
                
                # Ajustar ejes
                all_points = np.vstack((scaled_vector, transformed_vector, np.real(eigenvectors).T.flatten().reshape(-1, 3)))
                max_range = np.max(np.abs(all_points)) * 1.5
                
                self.ax.set_xlim([-max_range, max_range])
                self.ax.set_ylim([-max_range, max_range])
                self.ax.set_zlim([-max_range, max_range])
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante el cálculo:\n{str(e)}")
            import traceback
            traceback.print_exc()


