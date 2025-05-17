import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QCheckBox, QSpinBox, QGroupBox, 
                            QFormLayout, QSplitter, QTableWidget, QTableWidgetItem,
                            QComboBox, QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt
import sys
from sympy import symbols, sympify, lambdify, integrate, S
import random

class MonteCarloSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Integración por Monte Carlo")
        self.setStyleSheet("background-color: #F5F8FA; color: #333333; font-family: 'Helvetica Neue', sans-serif;")
        self.setGeometry(100, 100, 1200, 800)
        
        # Variables para almacenar resultados
        self.resultados = []
        self.valores_x = []
        self.valores_y = []
        self.puntos_dentro = []
        self.puntos_fuera = []
        self.valor_exacto = None
        self.area_mc = None
        self.func1 = None
        self.func2 = None
        
        # Layout principal con splitter
        main_layout = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo (controles)
        panel_izquierdo_widget = QWidget()
        panel_izquierdo = QVBoxLayout(panel_izquierdo_widget)
        panel_izquierdo.setContentsMargins(10, 10, 10, 10)
        panel_izquierdo.setSpacing(8)
        
        # Título
        titulo = QLabel("📊 Integración Monte Carlo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #2D3E50; margin-bottom: 10px;")
        panel_izquierdo.addWidget(titulo)
        
        # Grupo de configuración de la integración
        grupo_integracion = QGroupBox("Configuración de Integración")
        grupo_integracion.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 15px; }")
        form_integracion = QFormLayout()
        form_integracion.setVerticalSpacing(5)
        form_integracion.setHorizontalSpacing(5)
        
        # Selector de tipo de cálculo
        self.tipo_calculo = QComboBox()
        self.tipo_calculo.addItems(["Área bajo una curva", "Área entre dos curvas"])
        self.tipo_calculo.setStyleSheet(
            "padding: 5px; border-radius: 4px; background-color: #E4F0F6; "
            "color: #333333; border: 1px solid #B0D2E0;"
        )
        self.tipo_calculo.currentIndexChanged.connect(self.actualizar_formulario)
        form_integracion.addRow("Tipo de cálculo:", self.tipo_calculo)
        
        # Límites de integración
        estilo_input = (
            "padding: 5px; border-radius: 4px; background-color: #E4F0F6; "
            "color: #333333; border: 1px solid #B0D2E0;"
        )
        
        self.input_limite_a = QLineEdit("0")
        self.input_limite_a.setStyleSheet(estilo_input)
        form_integracion.addRow("Límite inferior (a):", self.input_limite_a)
        
        self.input_limite_b = QLineEdit("1")
        self.input_limite_b.setStyleSheet(estilo_input)
        form_integracion.addRow("Límite superior (b):", self.input_limite_b)
        
        # Funciones
        self.input_funcion1 = QLineEdit("x**2")
        self.input_funcion1.setStyleSheet(estilo_input)
        form_integracion.addRow("Función f(x):", self.input_funcion1)
        
        self.input_funcion2 = QLineEdit("0")
        self.input_funcion2.setStyleSheet(estilo_input)
        form_integracion.addRow("Función g(x):", self.input_funcion2)
        
        # Número de simulaciones
        self.input_simulaciones = QSpinBox()
        self.input_simulaciones.setRange(100, 1000000)
        self.input_simulaciones.setValue(10000)
        self.input_simulaciones.setSingleStep(1000)
        self.input_simulaciones.setStyleSheet(estilo_input)
        form_integracion.addRow("Simulaciones:", self.input_simulaciones)
        
        grupo_integracion.setLayout(form_integracion)
        panel_izquierdo.addWidget(grupo_integracion)
        
        # Opciones adicionales
        opciones_layout = QHBoxLayout()
        
        self.check_grid = QCheckBox("Mostrar cuadrícula")
        self.check_grid.setChecked(True)
        self.check_grid.setStyleSheet("font-size: 12px;")
        opciones_layout.addWidget(self.check_grid)
        
        self.check_puntos = QCheckBox("Mostrar todos los puntos")
        self.check_puntos.setChecked(False)
        self.check_puntos.setStyleSheet("font-size: 12px;")
        opciones_layout.addWidget(self.check_puntos)
        
        panel_izquierdo.addLayout(opciones_layout)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        self.boton_simular = QPushButton("Ejecutar Simulación")
        self.boton_simular.setCursor(Qt.PointingHandCursor)
        self.boton_simular.setStyleSheet("background-color: #0077B6; font-weight: bold; color: white; border-radius: 4px; padding: 8px;")
        self.boton_simular.clicked.connect(self.ejecutar_simulacion)
        botones_layout.addWidget(self.boton_simular)
        
        self.boton_guardar = QPushButton("Guardar Resultados")
        self.boton_guardar.setCursor(Qt.PointingHandCursor)
        self.boton_guardar.setStyleSheet("background-color: #28a745; font-weight: bold; color: white; border-radius: 4px; padding: 8px;")
        self.boton_guardar.clicked.connect(self.guardar_resultados)
        botones_layout.addWidget(self.boton_guardar)
        
        panel_izquierdo.addLayout(botones_layout)
        
        botones_layout2 = QHBoxLayout()
        
        self.boton_limpiar = QPushButton("Limpiar")
        self.boton_limpiar.setCursor(Qt.PointingHandCursor)
        self.boton_limpiar.setStyleSheet("background-color: #FF6B6B; font-weight: bold; color: white; border-radius: 4px; padding: 8px;")
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        botones_layout2.addWidget(self.boton_limpiar)
        
        self.boton_salir = QPushButton("Salir")
        self.boton_salir.setCursor(Qt.PointingHandCursor)
        self.boton_salir.setStyleSheet("background-color: #6c757d; font-weight: bold; color: white; border-radius: 4px; padding: 8px;")
        self.boton_salir.clicked.connect(self.close)
        botones_layout2.addWidget(self.boton_salir)
        
        panel_izquierdo.addLayout(botones_layout2)
        
        # Grupo de resultados
        self.grupo_resultados = QGroupBox("Resultados de la Simulación")
        self.grupo_resultados.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 15px; }")
        resultados_layout = QVBoxLayout()
        
        self.etiqueta_area_exacta = QLabel("Valor exacto de la integral: -")
        self.etiqueta_area_mc = QLabel("Aproximación Monte Carlo: -")
        self.etiqueta_error = QLabel("Error relativo: -")
        self.etiqueta_puntos = QLabel("Puntos simulados: -")
        
        for etiqueta in [self.etiqueta_area_exacta, self.etiqueta_area_mc, 
                        self.etiqueta_error, self.etiqueta_puntos]:
            etiqueta.setStyleSheet("font-size: 12px; padding: 2px;")
            resultados_layout.addWidget(etiqueta)
        
        self.grupo_resultados.setLayout(resultados_layout)
        panel_izquierdo.addWidget(self.grupo_resultados)
        
        # Tabla de convergencia
        self.tabla_convergencia = QTableWidget(0, 3)
        self.tabla_convergencia.setHorizontalHeaderLabels(['Simulaciones', 'Área Monte Carlo', 'Error Rel. (%)'])
        self.tabla_convergencia.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_convergencia.setStyleSheet("font-size: 12px;")
        panel_izquierdo.addWidget(self.tabla_convergencia)
        
        # Espacio flexible
        panel_izquierdo.addStretch()
        
        # Panel derecho (gráfica)
        panel_derecho = QWidget()
        panel_derecho_layout = QVBoxLayout(panel_derecho)
        panel_derecho_layout.setContentsMargins(0, 0, 0, 0)
        
        # Configuración de la figura para las gráficas
        self.figura = Figure(figsize=(6, 5), facecolor='white')
        self.canvas = FigureCanvas(self.figura)
        panel_derecho_layout.addWidget(self.canvas)
        
        # Añadir los paneles al splitter
        self.splitter.addWidget(panel_izquierdo_widget)
        self.splitter.addWidget(panel_derecho)
        
        # Establecer proporciones iniciales del splitter (30% controles, 70% gráfica)
        self.splitter.setSizes([400, 800])
        
        # Añadir el splitter al layout principal
        main_layout.addWidget(self.splitter)
        
        # Inicializar la gráfica vacía
        self.actualizar_grafica()
        
        # Establecer estado inicial
        self.actualizar_formulario()
    
    def actualizar_formulario(self):
        """Actualiza el formulario según el tipo de cálculo seleccionado"""
        if self.tipo_calculo.currentText() == "Área bajo una curva":
            self.input_funcion2.setText("0")
            self.input_funcion2.setEnabled(False)
        else:
            self.input_funcion2.setEnabled(True)
    
    def parsear_expresion(self, expresion_texto):
        """Convierte una expresión de texto a una función lambda"""
        try:
            x = symbols('x')
            expresion_sympy = sympify(expresion_texto)
            return lambdify(x, expresion_sympy, 'numpy')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al parsear la expresión: {str(e)}")
            return None
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación Monte Carlo"""
        try:
            # Parsear límites
            a = float(self.input_limite_a.text())
            b = float(self.input_limite_b.text())
            
            if a >= b:
                QMessageBox.warning(self, "Error", "El límite inferior debe ser menor que el superior.")
                return
            
            # Parsear funciones
            self.func1 = self.parsear_expresion(self.input_funcion1.text())
            self.func2 = self.parsear_expresion(self.input_funcion2.text())
            
            if not self.func1 or not self.func2:
                return
            
            # Calcular valor exacto de la integral
            x = symbols('x')
            expresion1 = sympify(self.input_funcion1.text())
            expresion2 = sympify(self.input_funcion2.text())
            
            # Integral exacta: ∫[a,b] (f(x) - g(x)) dx
            integral_exacta = integrate(expresion1 - expresion2, (x, a, b))
            self.valor_exacto = float(integral_exacta.evalf())
            
            # Ejecutar simulación Monte Carlo
            num_simulaciones = self.input_simulaciones.value()
            
            # Evaluar funciones en límites para encontrar rango vertical
            x_vals = np.linspace(a, b, 1000)
            y1_vals = self.func1(x_vals)
            y2_vals = self.func2(x_vals)
            
            # Encontrar el rango vertical para el rectángulo
            y_min = min(np.min(y2_vals), np.min(y1_vals))
            y_max = max(np.max(y1_vals), np.max(y2_vals))
            
            # Ajustar el rango vertical si es necesario
            if y_min > 0:
                y_min = 0
            if y_max < 0:
                y_max = 0
                
            # Añadir un pequeño margen al rango
            delta_y = (y_max - y_min) * 0.05
            y_min -= delta_y
            y_max += delta_y
            
            # Área del rectángulo que contiene la región
            area_rectangulo = (b - a) * (y_max - y_min)
            
            # Realizar simulación Monte Carlo
            puntos_dentro = 0
            
            # Generar puntos aleatorios
            random_x = np.random.uniform(a, b, num_simulaciones)
            random_y = np.random.uniform(y_min, y_max, num_simulaciones)
            
            # Variables para guardar puntos para la gráfica
            self.valores_x = random_x
            self.valores_y = random_y
            self.puntos_dentro = []
            self.puntos_fuera = []
            
            # Evaluar los puntos
            for i in range(num_simulaciones):
                x = random_x[i]
                y = random_y[i]
                
                valor_f1 = self.func1(x)
                valor_f2 = self.func2(x)
                
                # Determinar si el punto está dentro de la región
                if (y_min <= y <= y_max) and ((valor_f2 <= y <= valor_f1) if valor_f1 >= valor_f2 else (valor_f1 <= y <= valor_f2)):
                    puntos_dentro += 1
                    self.puntos_dentro.append((x, y))
                else:
                    self.puntos_fuera.append((x, y))
            
            # Calcular el área estimada
            self.area_mc = (puntos_dentro / num_simulaciones) * area_rectangulo
            
            # Calcular error relativo
            if self.valor_exacto != 0:
                error_relativo = abs((self.area_mc - self.valor_exacto) / self.valor_exacto) * 100
            else:
                error_relativo = float('inf') if self.area_mc != 0 else 0
            
            # Actualizar resultados
            self.etiqueta_area_exacta.setText(f"Valor exacto de la integral: {self.valor_exacto:.6f}")
            self.etiqueta_area_mc.setText(f"Aproximación Monte Carlo: {self.area_mc:.6f}")
            self.etiqueta_error.setText(f"Error relativo: {error_relativo:.4f}%")
            self.etiqueta_puntos.setText(f"Puntos simulados: {num_simulaciones} ({puntos_dentro} dentro)")
            
            # Actualizar tabla de convergencia
            fila = self.tabla_convergencia.rowCount()
            self.tabla_convergencia.insertRow(fila)
            self.tabla_convergencia.setItem(fila, 0, QTableWidgetItem(str(num_simulaciones)))
            self.tabla_convergencia.setItem(fila, 1, QTableWidgetItem(f"{self.area_mc:.6f}"))
            self.tabla_convergencia.setItem(fila, 2, QTableWidgetItem(f"{error_relativo:.4f}%"))
            self.tabla_convergencia.scrollToBottom()
            
            # Guardar resultado para uso posterior
            self.resultados.append({
                'simulaciones': num_simulaciones,
                'area_mc': self.area_mc,
                'error': error_relativo
            })
            
            # Actualizar gráfica
            self.actualizar_grafica()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la simulación: {str(e)}")
    
    def actualizar_grafica(self):
        """Actualiza la gráfica con los resultados"""
        self.figura.clear()
        
        # Si no hay resultados, mostrar gráfica vacía
        if not self.func1 or self.area_mc is None:
            ax = self.figura.add_subplot(111)
            ax.set_title("Integración por Monte Carlo")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.text(0.5, 0.5, "Ejecute una simulación para ver resultados", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        # Crear gráfica
        ax = self.figura.add_subplot(111)
        
        # Obtener límites
        a = float(self.input_limite_a.text())
        b = float(self.input_limite_b.text())
        
        # Generar puntos para las curvas
        x_vals = np.linspace(a, b, 1000)
        y1_vals = self.func1(x_vals)
        y2_vals = self.func2(x_vals)
        
        # Graficar funciones
        ax.plot(x_vals, y1_vals, 'b-', linewidth=2, label=f'f(x) = {self.input_funcion1.text()}')
        
        if self.tipo_calculo.currentText() == "Área entre dos curvas":
            ax.plot(x_vals, y2_vals, 'g-', linewidth=2, label=f'g(x) = {self.input_funcion2.text()}')
        
        # Rellenar área entre curvas
        ax.fill_between(x_vals, y1_vals, y2_vals, color='skyblue', alpha=0.4)
        
        # Mostrar puntos de la simulación si está activada la opción
        if self.check_puntos.isChecked() and self.puntos_dentro and self.puntos_fuera:
            # Separar coordenadas de puntos dentro
            x_dentro = [p[0] for p in self.puntos_dentro]
            y_dentro = [p[1] for p in self.puntos_dentro]
            
            # Separar coordenadas de puntos fuera
            x_fuera = [p[0] for p in self.puntos_fuera]
            y_fuera = [p[1] for p in self.puntos_fuera]
            
            # Mostrar solo una muestra de puntos para no sobrecargar la gráfica
            max_puntos = min(1000, len(self.puntos_dentro), len(self.puntos_fuera))
            
            # Seleccionar índices aleatorios
            if len(x_dentro) > max_puntos:
                indices = random.sample(range(len(x_dentro)), max_puntos)
                x_dentro_muestra = [x_dentro[i] for i in indices]
                y_dentro_muestra = [y_dentro[i] for i in indices]
            else:
                x_dentro_muestra = x_dentro
                y_dentro_muestra = y_dentro
                
            if len(x_fuera) > max_puntos:
                indices = random.sample(range(len(x_fuera)), max_puntos)
                x_fuera_muestra = [x_fuera[i] for i in indices]
                y_fuera_muestra = [y_fuera[i] for i in indices]
            else:
                x_fuera_muestra = x_fuera
                y_fuera_muestra = y_fuera
            
            # Graficar puntos
            ax.scatter(x_dentro_muestra, y_dentro_muestra, color='blue', s=5, alpha=0.5, label='Puntos dentro')
            ax.scatter(x_fuera_muestra, y_fuera_muestra, color='red', s=5, alpha=0.2, label='Puntos fuera')
        
        # Configurar gráfica
        ax.grid(self.check_grid.isChecked())
        ax.legend(loc='best')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        
        if self.tipo_calculo.currentText() == "Área bajo una curva":
            titulo = f"Área bajo la curva f(x) = {self.input_funcion1.text()}"
        else:
            titulo = f"Área entre f(x) = {self.input_funcion1.text()} y g(x) = {self.input_funcion2.text()}"
            
        ax.set_title(f"{titulo}\nValor exacto: {self.valor_exacto:.6f}, Monte Carlo: {self.area_mc:.6f}")
        
        # Ajustar vista para mostrar toda la región
        margin = 0.1
        xmargin = (b - a) * margin
        ax.set_xlim(a - xmargin, b + xmargin)
        
        # Encontrar límites verticales adecuados
        y_min = min(np.min(y1_vals), np.min(y2_vals))
        y_max = max(np.max(y1_vals), np.max(y2_vals))
        ymargin = (y_max - y_min) * margin
        ax.set_ylim(y_min - ymargin, y_max + ymargin)
        
        self.canvas.draw()
    
    def guardar_resultados(self):
        """Guarda los resultados como CSV e imagen"""
        if not self.resultados:
            QMessageBox.warning(self, "Sin datos", "No hay resultados para guardar.")
            return
        
        try:
            # Guardar como CSV
            opciones = QFileDialog.Options()
            nombre_archivo, _ = QFileDialog.getSaveFileName(
                self, "Guardar Resultados", "", 
                "Archivo CSV (*.csv);;Todos los archivos (*)",
                options=opciones)
                
            if nombre_archivo:
                # Asegurar que tenga extensión
                if not nombre_archivo.endswith('.csv'):
                    nombre_archivo += '.csv'
                
                # Crear contenido CSV
                lineas = ["simulaciones,area_monte_carlo,error_relativo"]
                for res in self.resultados:
                    lineas.append(f"{res['simulaciones']},{res['area_mc']},{res['error']}")
                
                # Guardar archivo
                with open(nombre_archivo, 'w') as f:
                    f.write('\n'.join(lineas))
                
                # Guardar imagen
                nombre_imagen = nombre_archivo.replace('.csv', '.png')
                self.figura.savefig(nombre_imagen, dpi=150, bbox_inches='tight')
                
                QMessageBox.information(self, "Guardado exitoso", 
                                      f"Datos guardados en {nombre_archivo}\nImagen guardada en {nombre_imagen}")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", 
                               f"No se pudieron guardar los resultados: {str(e)}")
    
    def limpiar_campos(self):
        """Limpia los campos y resultados"""
        # Reiniciar valores
        self.tipo_calculo.setCurrentIndex(0)
        self.input_limite_a.setText("0")
        self.input_limite_b.setText("1")
        self.input_funcion1.setText("x**2")
        self.input_funcion2.setText("0")
        self.input_simulaciones.setValue(10000)
        
        # Limpiar resultados
        self.resultados = []
        self.valores_x = []
        self.valores_y = []
        self.puntos_dentro = []
        self.puntos_fuera = []
        self.valor_exacto = None
        self.area_mc = None
        self.func1 = None
        self.func2 = None
        
        # Limpiar etiquetas
        self.etiqueta_area_exacta.setText("Valor exacto de la integral: -")
        self.etiqueta_area_mc.setText("Aproximación Monte Carlo: -")
        self.etiqueta_error.setText("Error relativo: -")
        self.etiqueta_puntos.setText("Puntos simulados: -")
        
        # Limpiar tabla
        self.tabla_convergencia.setRowCount(0)
        
        # Actualizar gráfica
        self.actualizar_grafica()
        
        # Actualizar formulario
        self.actualizar_formulario()

