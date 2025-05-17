import numpy as np
import sympy as sp
import scipy
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QListWidget, QGridLayout, QMessageBox, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import re

class Graficas_2d_3d(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráficas Avanzadas 2D y 3D")
        self.setStyleSheet("background-color: #F5F8FA; color: #333333; font-family: 'Helvetica Neue', sans-serif;")
        self.setGeometry(100, 100, 1200, 800)

        self.funciones_guardadas = []

        main_layout = QHBoxLayout(self)
        panel_izquierdo = QVBoxLayout()

        # Título y área de control
        panel_titulo = QVBoxLayout()
        titulo = QLabel("📊 Graficador de Funciones 2D/3D")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2D3E50; margin-bottom: 20px;")
        panel_titulo.addWidget(titulo)

        # Panel para funciones
        self.input_funcion = QLineEdit()
        self.input_funcion.setPlaceholderText("Escribe una función, por ejemplo: x**2 * exp(x) o sin(x)")
        self.input_funcion.setStyleSheet("padding: 14px; border-radius: 8px; background-color: #E4F0F6; color: #333333; border: 1px solid #B0D2E0; margin-bottom: 20px;")
        self.input_funcion.textChanged.connect(self.convertir_minusculas)
        panel_titulo.addWidget(self.input_funcion)

        # Lista de funciones guardadas
        self.lista_funciones = QListWidget()
        self.lista_funciones.setStyleSheet("background-color: #E4F0F6; color: #333333; border-radius: 8px; border: 1px solid #B0D2E0; margin-bottom: 20px;")
        panel_titulo.addWidget(self.lista_funciones)

        # Botón para agregar funciones
        boton_agregar = QPushButton("➕ Agregar función")
        boton_agregar.setCursor(Qt.PointingHandCursor)
        boton_agregar.setStyleSheet("background-color: #0077B6; color: white; font-weight: bold; border-radius: 8px; padding: 12px; margin-bottom: 20px;")
        boton_agregar.clicked.connect(self.agregar_funcion)
        panel_titulo.addWidget(boton_agregar)

        # Teclado de funciones matemáticas
        teclado_layout = QGridLayout()
        botones = [
            ('1', '1'), ('2', '2'), ('3', '3'), ('/', '/'),
            ('4', '4'), ('5', '5'), ('6', '6'), ('*', '*'),
            ('7', '7'), ('8', '8'), ('9', '9'), ('-', '-'),
            ('0', '0'), ('.', '.'), ('+', '+'), ('^', '**'),
            ('(', '('), (')', ')'), ('log', 'log('), ('exp', 'exp('),
            ('sin', 'sin('), ('cos', 'cos('), ('tan', 'tan('), ('√', 'sqrt('),
            ('x', 'x'), ('y', 'y'), ('π', 'pi'), ('e', 'e')
        ]
        for i, (text, value) in enumerate(botones):
            boton = QPushButton(text)
            boton.setStyleSheet("background-color: #0077B6; color: white; font-weight: bold; border-radius: 8px; padding: 12px;")
            boton.clicked.connect(self.crear_insertador(value))
            teclado_layout.addWidget(boton, i // 4, i % 4)
        panel_titulo.addLayout(teclado_layout)

        # Checkbox para mostrar/ocultar cuadrícula
        self.check_grid = QCheckBox("Mostrar cuadrícula")
        self.check_grid.setChecked(True)
        self.check_grid.setStyleSheet("font-size: 14px; margin: 10px 0;")
        panel_titulo.addWidget(self.check_grid)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.boton_2d = QPushButton("Mostrar Gráfica 2D")
        self.boton_2d.setCursor(Qt.PointingHandCursor)
        self.boton_2d.setStyleSheet("background-color: #0077B6; font-weight: bold; color: white; border-radius: 8px; padding: 12px;")
        self.boton_2d.clicked.connect(self.mostrar_grafica_2d)
        botones_layout.addWidget(self.boton_2d)

        self.boton_3d = QPushButton("Mostrar Gráfica 3D")
        self.boton_3d.setCursor(Qt.PointingHandCursor)
        self.boton_3d.setStyleSheet("background-color: #0077B6; font-weight: bold; color: white; border-radius: 8px; padding: 12px;")
        self.boton_3d.clicked.connect(self.mostrar_grafica_3d)
        botones_layout.addWidget(self.boton_3d)

        # Botón para guardar imagen
        self.boton_guardar = QPushButton("Guardar Imagen")
        self.boton_guardar.setCursor(Qt.PointingHandCursor)
        self.boton_guardar.setStyleSheet("background-color: #28a745; font-weight: bold; color: white; border-radius: 8px; padding: 12px;")
        self.boton_guardar.clicked.connect(self.guardar_imagen)
        botones_layout.addWidget(self.boton_guardar)

        self.boton_limpiar = QPushButton("Limpiar")
        self.boton_limpiar.setCursor(Qt.PointingHandCursor)
        self.boton_limpiar.setStyleSheet("background-color: #FF6B6B; font-weight: bold; color: white; border-radius: 8px; padding: 12px;")
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        botones_layout.addWidget(self.boton_limpiar)

        self.boton_volver = QPushButton("Volver")
        self.boton_volver.setCursor(Qt.PointingHandCursor)
        self.boton_volver.setStyleSheet("background-color: #0077B6; font-weight: bold; color: white; border-radius: 8px; padding: 12px;")
        self.boton_volver.clicked.connect(self.volver)
        botones_layout.addWidget(self.boton_volver)

        panel_titulo.addLayout(botones_layout)
        panel_izquierdo.addLayout(panel_titulo)

        # Configuración de la figura para las gráficas
        self.figura = Figure(figsize=(6, 5), facecolor='white')
        self.canvas = FigureCanvas(self.figura)
        main_layout.addLayout(panel_izquierdo)
        main_layout.addWidget(self.canvas)

    def crear_insertador(self, valor):
        def insertar():
            self.input_funcion.insert(valor)
        return insertar

    def convertir_minusculas(self, texto):
        cursor_pos = self.input_funcion.cursorPosition()
        self.input_funcion.blockSignals(True)
        self.input_funcion.setText(texto.lower())
        self.input_funcion.setCursorPosition(cursor_pos)
        self.input_funcion.blockSignals(False)

    def preprocesar_funcion(self, expr):
        # Reemplazos básicos más robustos
        expr = expr.replace('^', '**')
        
        # Manejar 'e' como constante de Euler
        expr = re.sub(r'(?<![a-zA-Z_])e(?![a-zA-Z_\(])', 'exp(1)', expr)
        
        # Reemplazar π con pi
        expr = expr.replace('π', 'pi')
        
        # Multiplicación implícita: números seguidos de variables o paréntesis
        # Este es el cambio clave para casos como 2x+3
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        
        # Otras multiplicaciones implícitas
        expr = re.sub(r'(\d)(\()', r'\1*\2', expr)
        expr = re.sub(r'(\))([a-zA-Z0-9])', r'\1*\2', expr)
        expr = re.sub(r'(\))(\()', r'\1*\2', expr)
        
        # Asegurar que las funciones matemáticas tengan paréntesis correctos
        expr = re.sub(r'sin\s*(\w)', r'sin(\1)', expr)
        expr = re.sub(r'cos\s*(\w)', r'cos(\1)', expr)
        expr = re.sub(r'tan\s*(\w)', r'tan(\1)', expr)
        expr = re.sub(r'log\s*(\w)', r'log(\1)', expr)
        expr = re.sub(r'exp\s*(\w)', r'exp(\1)', expr)
        expr = re.sub(r'sqrt\s*(\w)', r'sqrt(\1)', expr)
        
        return expr

    def agregar_funcion(self):
        texto = self.input_funcion.text()
        if texto.strip() == "":
            return
        self.funciones_guardadas.append(texto)
        self.lista_funciones.addItem(texto)
        self.input_funcion.clear()
        QMessageBox.information(self, "Función guardada", f"La función '{texto}' ha sido guardada correctamente.")

    def mostrar_grafica_2d(self):
        if not self.funciones_guardadas:
            QMessageBox.warning(self, "Sin funciones", "Primero agrega al menos una función.")
            return

        x = sp.Symbol('x')
        x_val = np.linspace(-10, 10, 400)
        self.figura.clear()
        ax = self.figura.add_subplot(111)

        for func_str in self.funciones_guardadas:
            try:
                # Aplicamos el preprocesamiento antes de usar sympy
                expr = self.preprocesar_funcion(func_str)
                
                if 'y' in expr:
                    QMessageBox.warning(self, "Error", f"La función '{func_str}' contiene 'y'. Solo se permiten funciones de x en gráficas 2D.")
                    continue
                
                # Usar sympify de forma más directa, similar al código de tu amigo
                funcion = sp.sympify(expr)
                f = sp.lambdify(x, funcion, modules=['numpy'])
                
                y_val = f(x_val)
                
                # Filtrar valores infinitos o NaN para evitar errores de graficación
                valid_indices = np.isfinite(y_val)
                if not np.any(valid_indices):
                    QMessageBox.warning(self, "Error", f"La función '{func_str}' genera solo valores infinitos o no numéricos.")
                    continue
                    
                ax.plot(x_val[valid_indices], y_val[valid_indices], label=f"y = {func_str}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo graficar: {func_str}\nError: {str(e)}")
                continue

        # Configurar si se muestra la cuadrícula según el estado del checkbox
        ax.grid(self.check_grid.isChecked())
        ax.legend(loc='upper left')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Gráfica 2D')
        self.canvas.draw()

    def mostrar_grafica_3d(self):
        if not self.funciones_guardadas:
            QMessageBox.warning(self, "Sin funciones", "Primero agrega al menos una función para graficar en 3D.")
            return

        x, y = sp.symbols('x y')
        x_val = np.linspace(-5, 5, 100)
        y_val = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x_val, y_val)

        self.figura.clear()
        ax = self.figura.add_subplot(111, projection='3d')

        for func_str in self.funciones_guardadas:
            try:
                # Aplicamos el preprocesamiento antes de usar sympy
                expr = self.preprocesar_funcion(func_str)
                
                # Usar sympify de forma más directa
                funcion = sp.sympify(expr)
                free_symbols = [str(sym) for sym in funcion.free_symbols]
                
                if 'y' not in free_symbols:
                    # Si solo depende de x, graficamos una superficie extendida en el eje y
                    f = sp.lambdify(x, funcion, modules=['numpy'])
                    Z = np.zeros_like(X)
                    for i in range(Z.shape[0]):
                        try:
                            Z[i, :] = f(X[i, :])
                        except Exception:
                            Z[i, :] = np.nan
                else:
                    # Si depende de x e y, graficamos normalmente
                    f = sp.lambdify((x, y), funcion, modules=['numpy'])
                    try:
                        Z = f(X, Y)
                    except Exception:
                        QMessageBox.warning(self, "Error", f"No se pudo evaluar la función '{func_str}' con valores x,y.")
                        continue
                
                # Verificar que Z contiene valores numéricos válidos
                if np.isnan(Z).all() or np.isinf(Z).all():
                    QMessageBox.warning(self, "Error", f"La función '{func_str}' produce solo valores no numéricos o infinitos.")
                    continue
                    
                # Reemplazar valores infinitos o NaN con NaN para evitar errores de graficación
                Z = np.where(np.isfinite(Z), Z, np.nan)
                
                # Limitar el rango de Z para evitar gráficas distorsionadas
                max_z = 50
                Z = np.clip(Z, -max_z, max_z)
                    
                # Usar un color diferente para cada función
                colors = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
                color_index = self.funciones_guardadas.index(func_str) % len(colors)
                
                surf = ax.plot_surface(X, Y, Z, cmap=colors[color_index], edgecolor='none', alpha=0.7)
                
                # Añadir una barra de color para esta superficie
                if 'y' in free_symbols:
                    func_label = f"z = {func_str}"
                else:
                    func_label = f"z = {func_str} (extendido en y)"
                self.figura.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label=func_label)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo graficar en 3D: {func_str}\nError: {str(e)}")
                continue

        # Configurar si se muestra la cuadrícula según el estado del checkbox
        ax.grid(self.check_grid.isChecked())
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Gráfica 3D')
        self.canvas.draw()

    def guardar_imagen(self):
        """Guarda la gráfica actual como imagen"""
        if not hasattr(self.figura, 'axes') or not self.figura.axes:
            QMessageBox.warning(self, "Sin gráfica", "Primero debes generar una gráfica.")
            return
            
        opciones = QFileDialog.Options()
        nombre_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar Gráfica", "", 
            "Imágenes PNG (*.png);;Imágenes JPG (*.jpg);;Todos los archivos (*)",
            options=opciones)
            
        if nombre_archivo:
            try:
                # Asegurar que tenga extensión
                if not (nombre_archivo.endswith('.png') or nombre_archivo.endswith('.jpg')):
                    nombre_archivo += '.png'
                
                self.figura.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
                QMessageBox.information(self, "Guardado exitoso", 
                                      f"La gráfica se ha guardado como {nombre_archivo}")
            except Exception as e:
                QMessageBox.critical(self, "Error al guardar", 
                                   f"No se pudo guardar la imagen: {str(e)}")

    def limpiar_campos(self):
        self.input_funcion.clear()
        self.lista_funciones.clear()
        self.funciones_guardadas.clear()
        # También limpia la gráfica actual
        self.figura.clear()
        self.canvas.draw()

    def volver(self):
        self.close()