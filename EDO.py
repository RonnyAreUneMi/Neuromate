import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sympy as sp
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QFrame, QGroupBox, QHeaderView,
    QComboBox, QToolBar, QAction
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
matplotlib.use('Qt5Agg')
plt.style.use('seaborn-v0_8-whitegrid')


class EDOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resolución de EDO")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #F6F1F1;
                color: #333333;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLabel {
                color: #19376D;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #146C94;
            }
            QPushButton {
                background-color: #19A7CE;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #146C94;
            }
            QPushButton:pressed {
                background-color: #0b2447;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                gridline-color: #AEFEFF;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #AEFEFF;
                color: #0b2447;
            }
            QHeaderView::section {
                background-color: #19A7CE;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                padding: 5px;
                color: #333333;
            }
            QGroupBox {
                border: 2px solid #19A7CE;
                border-radius: 10px;
                margin-top: 15px;
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
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #19A7CE;
                selection-background-color: #AEFEFF;
                selection-color: #0b2447;
            }
            QToolBar {
                background-color: #F6F1F1;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                spacing: 3px;
            }
            QToolButton {
                background-color: #F6F1F1;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #AEFEFF;
            }
            QToolButton:pressed {
                background-color: #19A7CE;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Título
        title_layout = QHBoxLayout()
        title = QLabel("Resolución de Ecuaciones Diferenciales Ordinarias")
        title.setStyleSheet("font-size: 24px; color: #19A7CE; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Parámetros de entrada
        input_group = QGroupBox("Parámetros de Entrada")
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)

        self.func_input = QLineEdit("x + y")
        self.func_input.setPlaceholderText("Ejemplo: x + y")

        self.x0_input = QDoubleSpinBox()
        self.x0_input.setRange(-1000, 1000)
        self.x0_input.setValue(0.0)
        self.x0_input.setDecimals(4)

        self.y0_input = QDoubleSpinBox()
        self.y0_input.setRange(-1000, 1000)
        self.y0_input.setValue(1.0)
        self.y0_input.setDecimals(4)

        self.n_input = QSpinBox()
        self.n_input.setRange(1, 1000)
        self.n_input.setValue(5)

        self.h_input = QDoubleSpinBox()
        self.h_input.setRange(0.01, 10.0)
        self.h_input.setValue(0.1)
        self.h_input.setSingleStep(0.01)
        self.h_input.setDecimals(4)

        # Selector de método
        self.method_selector = QComboBox()
        self.method_selector.addItems(["Todos los métodos", "Euler", "Heun", "Runge-Kutta 4", "Taylor 2° orden"])

        params = [
            ("f(x, y):", self.func_input),
            ("x₀:", self.x0_input),
            ("y₀:", self.y0_input),
            ("Pasos (n):", self.n_input),
            ("Paso (h):", self.h_input),
            ("Método:", self.method_selector)
        ]

        for label_text, widget in params:
            param_layout = QVBoxLayout()
            label = QLabel(label_text)
            param_layout.addWidget(label)
            param_layout.addWidget(widget)
            input_layout.addLayout(param_layout)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Botón calcular
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        self.calc_btn = QPushButton("Calcular Soluciones")
        self.calc_btn.setIcon(QIcon("img/edo.png"))
        self.calc_btn.setMinimumHeight(40)
        self.calc_btn.setIconSize(QSize(24, 24))
        self.calc_btn.clicked.connect(self.calcular)
        button_layout.addStretch()
        button_layout.addWidget(self.calc_btn)
        button_layout.addStretch()
        main_layout.addWidget(button_frame)

        # Tabla de resultados
        self.results_group = QGroupBox("Resultados Numéricos")
        results_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #F0F8FF;
            }
            QTableWidget::item {
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
            QHeaderView::section {
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.verticalHeader().setDefaultSectionSize(30)
        results_layout.addWidget(self.table)
        self.results_group.setLayout(results_layout)

        # Gráfica
        self.graph_group = QGroupBox("Representación Gráfica")
        graph_layout = QVBoxLayout()
        
        # Crear figura y lienzo para Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.figure.patch.set_facecolor('#F6F1F1')
        self.ax.set_facecolor('#FFFFFF')
        self.canvas = FigureCanvas(self.figure)
        
        # Agregar barra de herramientas de navegación para interactividad
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #F6F1F1;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                spacing: 5px;
                padding: 2px;
            }
        """)
        
        # Personalizar la barra de herramientas
        self.customize_toolbar()
        
        # Agregar componentes al layout
        graph_layout.addWidget(self.toolbar)
        graph_layout.addWidget(self.canvas)
        self.graph_group.setLayout(graph_layout)

        # Layout horizontal tabla + gráfica
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.results_group, 2)
        content_layout.addWidget(self.graph_group, 3)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def customize_toolbar(self):
        """Personaliza la barra de herramientas de navegación"""
        # Limpiando los espaciadores existentes y reorganizando la barra
        actions = self.toolbar.actions()
        
        # Agregar tooltips en español
        tooltips = {
            'Home': 'Restaurar vista original',
            'Back': 'Volver a vista anterior',
            'Forward': 'Ir a vista siguiente',
            'Pan': 'Mover gráfica (arrastrar)',
            'Zoom': 'Zoom rectangular',
            'Subplots': 'Configurar subplots',
            'Save': 'Guardar la figura'
        }
        
        for action in actions:
            if action.text() in tooltips:
                action.setToolTip(tooltips[action.text()])
                # Hacer que los iconos sean ligeramente más grandes
                if action.icon().pixmap(1, 1).width() > 0:  # verificar que tenga un icono
                    icon = action.icon()
                    pixmap = icon.pixmap(24, 24)  # tamaño ligeramente mayor
                    action.setIcon(QIcon(pixmap))
    
    def calcular(self):
        try:
            func = self.func_input.text()
            x0 = self.x0_input.value()
            y0 = self.y0_input.value()
            n = self.n_input.value()
            h = self.h_input.value()
            selected_method = self.method_selector.currentText()

            x_sym, y_sym = sp.symbols("x y")
            f_expr = sp.sympify(func)
            f_lambdified = sp.lambdify((x_sym, y_sym), f_expr, modules=["numpy"])

            # Definir métodos de solución
            def euler():
                x_vals, y_vals = [x0], [y0]
                for _ in range(n):
                    y = y_vals[-1] + h * f_lambdified(x_vals[-1], y_vals[-1])
                    x = x_vals[-1] + h
                    x_vals.append(x)
                    y_vals.append(y)
                return x_vals, y_vals

            def heun():
                x_vals, y_vals = [x0], [y0]
                for _ in range(n):
                    x, y = x_vals[-1], y_vals[-1]
                    y_pred = y + h * f_lambdified(x, y)
                    y_new = y + h/2 * (f_lambdified(x, y) + f_lambdified(x + h, y_pred))
                    x_vals.append(x + h)
                    y_vals.append(y_new)
                return x_vals, y_vals

            def rk4():
                x_vals, y_vals = [x0], [y0]
                for _ in range(n):
                    x, y = x_vals[-1], y_vals[-1]
                    k1 = h * f_lambdified(x, y)
                    k2 = h * f_lambdified(x + h/2, y + k1/2)
                    k3 = h * f_lambdified(x + h/2, y + k2/2)
                    k4 = h * f_lambdified(x + h, y + k3)
                    y_new = y + (k1 + 2*k2 + 2*k3 + k4)/6
                    x_vals.append(x + h)
                    y_vals.append(y_new)
                return x_vals, y_vals

            def taylor2():
                x_vals, y_vals = [x0], [y0]
                fy = sp.diff(f_expr, y_sym)
                fx = sp.diff(f_expr, x_sym)
                f_deriv = sp.lambdify((x_sym, y_sym), fx + fy * f_expr, modules=["numpy"])
                for _ in range(n):
                    x, y = x_vals[-1], y_vals[-1]
                    y_new = y + h * f_lambdified(x, y) + (h**2 / 2) * f_deriv(x, y)
                    x_vals.append(x + h)
                    y_vals.append(y_new)
                return x_vals, y_vals

            # Calcular según el método seleccionado
            results = {}
            method_names = []
            colors = {"Euler": "#0b2447", "Heun": "#19376D", "Runge-Kutta 4": "#19A7CE", "Taylor 2° orden": "#576CBC"}
            markers = {"Euler": "o", "Heun": "s", "Runge-Kutta 4": "^", "Taylor 2° orden": "x"}

            if selected_method == "Todos los métodos" or selected_method == "Euler":
                results["Euler"] = euler()
                method_names.append("Euler")
            
            if selected_method == "Todos los métodos" or selected_method == "Heun":
                results["Heun"] = heun()
                method_names.append("Heun")
            
            if selected_method == "Todos los métodos" or selected_method == "Runge-Kutta 4":
                results["Runge-Kutta 4"] = rk4()
                method_names.append("Runge-Kutta 4")
            
            if selected_method == "Todos los métodos" or selected_method == "Taylor 2° orden":
                results["Taylor 2° orden"] = taylor2()
                method_names.append("Taylor 2° orden")

            # Configurar tabla según el método seleccionado
            self.table.clearContents()
            self.table.setColumnCount(len(method_names) + 1)  # +1 para la columna x
            
            headers = ["x"] + method_names
            self.table.setHorizontalHeaderLabels(headers)
            
            # Usamos el primer método para determinar la longitud de los datos
            first_method = method_names[0]
            x_vals = results[first_method][0]
            self.table.setRowCount(len(x_vals))

            # Llenar la tabla con datos
            for i in range(len(x_vals)):
                # Columna x
                x_item = QTableWidgetItem(f"{x_vals[i]:.4f}")
                x_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 0, x_item)
                
                # Columnas de métodos
                for col, method in enumerate(method_names, 1):
                    y_vals = results[method][1]
                    y_item = QTableWidgetItem(f"{y_vals[i]:.6f}")
                    y_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, col, y_item)

            self.table.resizeColumnsToContents()

            # Gráfica
            self.ax.clear()
            
            for method in method_names:
                x_vals, y_vals = results[method]
                self.ax.plot(x_vals, y_vals, f"{markers[method]}-", 
                             color=colors[method], label=method, markersize=6)

            self.ax.set_xlabel("x", fontweight='bold', fontsize=12)
            self.ax.set_ylabel("y", fontweight='bold', fontsize=12)
            
            if selected_method == "Todos los métodos":
                title = "Comparación de Métodos Numéricos"
            else:
                title = f"Solución por Método de {selected_method}"
                
            self.ax.set_title(title, fontsize=16, fontweight='bold', color="#0b2447")
            self.ax.legend(loc='best', frameon=True, framealpha=0.9, fontsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)

            for spine in self.ax.spines.values():
                spine.set_color('#19A7CE')
                spine.set_linewidth(1.5)

            # Habilitar los eventos de interacción con la gráfica
            self.canvas.draw()
            
            # Mostrar mensaje de éxito
            if selected_method == "Todos los métodos":
                msg = "Todos los métodos numéricos han sido calculados exitosamente."
            else:
                msg = f"El método de {selected_method} ha sido calculado exitosamente."
                
            QMessageBox.information(self, "Cálculo Completado", msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante el cálculo:\n{str(e)}")
            import traceback
            traceback.print_exc()


