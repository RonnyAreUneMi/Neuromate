import sys
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QHBoxLayout, QSplitter, QScrollArea,
    QStackedWidget, QGroupBox, QComboBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QEvent
from oppoli import MenuPolinomios
from calculadora import MatrixCalculator, SistemasLineales
from opvect import CalculadoraVectores
from acercade import AcercaDe
from fun2d import Graficas_2d_3d
from EDO import EDOApp
from predictivo import Prediccion
from vyvpropios import vyvpropios
from aleatorios import numram
from montecarlo import MonteCarloSimulator 
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class MenuButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setIconSize(QSize(28, 28))
        
        if icon_path:
            self.setIcon(QIcon(resource_path(icon_path)))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #0b2447;
                color: white;
                border: none;
                border-radius: 0px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #19376D;
            }
            QPushButton:pressed {
                background-color: #19A7CE;
            }
            QPushButton:checked {
                background-color: #19A7CE;
                border-left: 4px solid #AEFEFF;
            }
        """)
        self.setCheckable(True)

class NeuroMate(QWidget):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        app.installEventFilter(self)
        # Creamos instancias de los componentes
        self.polinomios_widget = None
        self.vectores_widget = None
        self.graficas_widget = None
        self.acerca_widget = None
        self.edo_widget = None
        self.matriz_calc_widget = None
        self.sistemas_lineales_widget = None
        self.prediccion_widget = None  # Nueva instancia para el sistema de predicción
        # Instancia para Vectores y Valores propios
        self.vyv_widget = None  # V&V propios
        # Instancias para los nuevos componentes
        self.numgen_widget = None  # Generación de números
        self.montecarlo_widget = None  # Habilitado Montecarlo
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("NeuroMate - Sistema Matemático")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(QIcon(resource_path("img/icon.ico")))
        self.setStyleSheet("""
            QWidget {
                background-color: #F6F1F1;
                color: #333;
                font-family: 'Segoe UI';
            }
            QLabel#title {
                font-weight: bold;
                font-size: 24px;
                color: #19A7CE;
            }
            QFrame#sidebar {
                background-color: #0b2447;
                border-right: 1px solid #19A7CE;
            }
            QFrame#content {
                background-color: #FFFFFF;
                border: none;
            }
            QGroupBox {
                border: 2px solid #19A7CE;
                border-radius: 10px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                color: #19A7CE;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox {
                background-color: #19376D;
                color: white;
                border: 1px solid #19A7CE;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                margin-left: 30px;
                margin-right: 5px;
                min-height: 30px;
            }
            QComboBox:hover {
                background-color: #146C94;
            }
            QComboBox QAbstractItemView {
                background-color: #19376D;
                color: white;
                selection-background-color: #19A7CE;
                selection-color: white;
                border: 1px solid #19A7CE;
            }
        """)
        
        # Layout principal con splitter
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(250)
        self.sidebar.setMaximumWidth(250)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setWidget(self.sidebar)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sidebar_scroll.setStyleSheet("QScrollArea { border: none; }")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo container
        logo_container = QFrame()
        logo_container.setStyleSheet("background-color: #0b2447; padding: 20px;")
        logo_layout = QHBoxLayout(logo_container)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("img/head.png"))
        logo_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        sidebar_layout.addWidget(logo_container)
        
        # BOTONES DE MENÚ
        self.btn_inicio = MenuButton("Inicio", "img/icon.png")
        self.btn_matrices = MenuButton("Matrices", "img/matrices.png")
        
        # ComboBox para opciones de matrices (inicialmente oculto)
        self.matrices_options = QComboBox()
        self.matrices_options.addItem("Seleccione una opción")
        self.matrices_options.addItem("Calculadora de Matrices")
        self.matrices_options.addItem("Sistemas Lineales")
        self.matrices_options.setVisible(False)
        self.matrices_options.currentIndexChanged.connect(self.handle_matrices_option)
        
        self.btn_polinomios = MenuButton("Polinomios", "img/polinomios.png")
        self.btn_vectores = MenuButton("Vectores", "img/vectores.png")
        self.btn_funciones = MenuButton("Funciones", "img/funcion.webp")
        self.btn_edo = MenuButton("EDO", "img/edo.png")
        self.btn_vyv = MenuButton("V&V Propios", "img/vv.png")
        self.btn_numgen = MenuButton("Generación de Números", "img/random.png")
        self.btn_montecarlo = MenuButton("Montecarlo", "img/montecarlo.png")
        self.btn_prediccion = MenuButton("Sistema de Predicción", "img/predict.png")
        self.btn_acerca = MenuButton("Acerca de", "img/acerd.png")
        
        sidebar_layout.addWidget(self.btn_inicio)
        sidebar_layout.addWidget(self.btn_matrices)
        sidebar_layout.addWidget(self.matrices_options)
        sidebar_layout.addWidget(self.btn_polinomios)
        sidebar_layout.addWidget(self.btn_vectores)
        sidebar_layout.addWidget(self.btn_funciones)
        sidebar_layout.addWidget(self.btn_edo)
        
        # AGREGAR BOTÓN V&V PROPIOS
        sidebar_layout.addWidget(self.btn_vyv)
        # AGREGAR NUEVO BOTÓN GENERACIÓN DE NÚMEROS (HABILITADO)
        sidebar_layout.addWidget(self.btn_numgen)
        # AGREGAR BOTÓN MONTECARLO (HABILITADO)
        sidebar_layout.addWidget(self.btn_montecarlo)
        
        sidebar_layout.addWidget(self.btn_prediccion)
        sidebar_layout.addWidget(self.btn_acerca)
        sidebar_layout.addStretch(1)
        
        self.btn_salir = MenuButton("Salir", "img/salir.png")
        self.btn_salir.setStyleSheet("""
            QPushButton {
                background-color: #E94560;
                color: white;
                border: none;
                border-radius: 0px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sidebar_layout.addWidget(self.btn_salir)
        
        # Panel de contenido
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content")
        self.stacked_widget = QStackedWidget()
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stacked_widget)
        
        # Agregar widgets al splitter
        splitter.addWidget(sidebar_scroll)
        splitter.addWidget(self.content_frame)
        splitter.setSizes([250, 950])
        
        # Crear páginas para el stacked widget
        self.page_inicio = self.crear_pagina_inicio()
        self.page_matrices = self.crear_pagina_matrices_menu()
        
        # Añadir páginas iniciales al stacked widget
        self.stacked_widget.addWidget(self.page_inicio)
        self.stacked_widget.addWidget(self.page_matrices)
        
        # Conectar botones
        self.btn_inicio.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_matrices.clicked.connect(self.mostrar_matrices_menu)
        self.btn_polinomios.clicked.connect(self.mostrar_polinomios)
        self.btn_vectores.clicked.connect(self.mostrar_vectores)
        self.btn_funciones.clicked.connect(self.mostrar_graficas)
        self.btn_edo.clicked.connect(self.mostrar_edo)
        
        # CONECTAR BOTÓN V&V PROPIOS
        self.btn_vyv.clicked.connect(self.mostrar_vyv)
        # CONECTAR NUEVO BOTÓN GENERACIÓN DE NÚMEROS (HABILITADO)
        self.btn_numgen.clicked.connect(self.mostrar_numgen)
        # CONECTAR BOTÓN MONTECARLO (HABILITADO)
        self.btn_montecarlo.clicked.connect(self.mostrar_montecarlo)
        
        self.btn_prediccion.clicked.connect(self.mostrar_prediccion)
        self.btn_acerca.clicked.connect(self.mostrar_acerca)
        self.btn_salir.clicked.connect(self.close)
        
        # Configuración inicial
        self.btn_inicio.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
    
    def cambiar_pagina(self, index):
        self.activar_menu(self.sender())
        self.stacked_widget.setCurrentIndex(index)
    
    def activar_menu(self, boton_activo):
        # Desactivar todos los botones
        for btn in [self.btn_inicio, self.btn_matrices, self.btn_polinomios, 
                   self.btn_vectores, self.btn_funciones, self.btn_edo, 
                   self.btn_vyv, self.btn_numgen, self.btn_montecarlo, self.btn_prediccion, self.btn_acerca]:
            # Incluir los nuevos botones (actualizado para incluir btn_vyv, btn_numgen y btn_montecarlo)
            btn.setChecked(False)
        
        # Activar el botón seleccionado
        if boton_activo:
            boton_activo.setChecked(True)
    
    def mostrar_matrices_menu(self):
        self.activar_menu(self.btn_matrices)
        # Mostrar el ComboBox
        self.matrices_options.setVisible(True)
        self.matrices_options.setCurrentIndex(0)
        # Mostrar la página de selección de matrices
        self.stacked_widget.setCurrentIndex(1)
    
    def handle_matrices_option(self, index):
        if index == 0:  # "Seleccione una opción"
            return
        elif index == 1:  # "Calculadora de Matrices"
            self.mostrar_calculadora_matrices()
        elif index == 2:  # "Sistemas Lineales"
            self.mostrar_sistemas_lineales()
    
    def mostrar_calculadora_matrices(self):
        # Si la instancia de calculadora de matrices ya existe, mostramos esa
        if self.matriz_calc_widget is None:
            try:
                self.matriz_calc_widget = MatrixCalculator()
                self.matriz_calc_widget.setWindowFlags(Qt.Widget)  # Evita que se muestre como ventana separada
                self.stacked_widget.addWidget(self.matriz_calc_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Calculadora de Matrices: {str(e)}")
                return
        
        # Encontrar el índice del widget de calculadora de matrices
        index = self.stacked_widget.indexOf(self.matriz_calc_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_sistemas_lineales(self):
        # Si la instancia de sistemas lineales ya existe, mostramos esa
        if self.sistemas_lineales_widget is None:
            try:
                self.sistemas_lineales_widget = SistemasLineales()
                self.sistemas_lineales_widget.setWindowFlags(Qt.Widget)  # Evita que se muestre como ventana separada
                self.stacked_widget.addWidget(self.sistemas_lineales_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Sistemas Lineales: {str(e)}")
                return
        
        # Encontrar el índice del widget de sistemas lineales
        index = self.stacked_widget.indexOf(self.sistemas_lineales_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_polinomios(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_polinomios)
        
        # Si la instancia de polinomios ya existe, mostramos esa
        if self.polinomios_widget is None:
            try:
                self.polinomios_widget = MenuPolinomios()
                self.stacked_widget.addWidget(self.polinomios_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Polinomios: {str(e)}")
                return
        
        # Encontrar el índice del widget de polinomios
        index = self.stacked_widget.indexOf(self.polinomios_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_vectores(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_vectores)
        
        # Si la instancia de vectores ya existe, mostramos esa
        if self.vectores_widget is None:
            try:
                self.vectores_widget = CalculadoraVectores()
                self.stacked_widget.addWidget(self.vectores_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Vectores: {str(e)}")
                return
        
        # Encontrar el índice del widget de vectores
        index = self.stacked_widget.indexOf(self.vectores_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_graficas(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_funciones)
        
        # Si la instancia de gráficas ya existe, mostramos esa
        if self.graficas_widget is None:
            try:
                self.graficas_widget = Graficas_2d_3d()
                self.stacked_widget.addWidget(self.graficas_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Gráficas: {str(e)}")
                return
        
        # Encontrar el índice del widget de gráficas
        index = self.stacked_widget.indexOf(self.graficas_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_edo(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_edo)

        if self.edo_widget is None:
            try:
                self.edo_widget = EDOApp()
                self.stacked_widget.addWidget(self.edo_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar EDO: {str(e)}")
                return

        index = self.stacked_widget.indexOf(self.edo_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    # FUNCIÓN PARA V&V PROPIOS
    def mostrar_vyv(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_vyv)
        
        # Si la instancia de V&V ya existe, mostramos esa
        if self.vyv_widget is None:
            try:
                # Inicializamos el módulo de vectores y valores propios
                self.vyv_widget = vyvpropios()
                self.stacked_widget.addWidget(self.vyv_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar V&V Propios: {str(e)}")
                return
        
        # Encontrar el índice del widget de V&V
        index = self.stacked_widget.indexOf(self.vyv_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    # NUEVA FUNCIÓN HABILITADA PARA GENERACIÓN DE NÚMEROS
    def mostrar_numgen(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_numgen)
        
        # Si la instancia de Generación de Números ya existe, mostramos esa
        if self.numgen_widget is None:
            try:
                # Inicializamos el módulo de generación de números aleatorios
                self.numgen_widget = numram()
                self.stacked_widget.addWidget(self.numgen_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Generación de Números: {str(e)}")
                return
        
        # Encontrar el índice del widget de Generación de Números
        index = self.stacked_widget.indexOf(self.numgen_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    # FUNCIÓN HABILITADA PARA MONTECARLO
    def mostrar_montecarlo(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_montecarlo)
        
        # Si la instancia de Montecarlo ya existe, mostramos esa
        if self.montecarlo_widget is None:
            try:
                # Inicializamos el módulo MonteCarloSimulator
                self.montecarlo_widget = MonteCarloSimulator()
                self.stacked_widget.addWidget(self.montecarlo_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Montecarlo: {str(e)}")
                return
        
        # Encontrar el índice del widget de Montecarlo
        index = self.stacked_widget.indexOf(self.montecarlo_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_prediccion(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_prediccion)
        
        # Si la instancia de predicción ya existe, mostramos esa
        if self.prediccion_widget is None:
            try:
                self.prediccion_widget = Prediccion()
                self.stacked_widget.addWidget(self.prediccion_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Sistema de Predicción: {str(e)}")
                return
        
        # Encontrar el índice del widget de predicción
        index = self.stacked_widget.indexOf(self.prediccion_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def mostrar_acerca(self):
        # Ocultar ComboBox de matrices
        self.matrices_options.setVisible(False)
        self.activar_menu(self.btn_acerca)
        
        # Si la instancia de acerca ya existe, mostramos esa
        if self.acerca_widget is None:
            try:
                self.acerca_widget = AcercaDe()
                self.stacked_widget.addWidget(self.acerca_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar Acerca de: {str(e)}")
                return
        
        # Encontrar el índice del widget de acerca
        index = self.stacked_widget.indexOf(self.acerca_widget)
        self.stacked_widget.setCurrentIndex(index)
    
    def eventFilter(self, obj, event):
        try:
            return super().eventFilter(obj, event)
        except Exception as e:
            error_message = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Error en NeuroMate", error_message)
            return True
    
    def crear_pagina_inicio(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Contenedor central para la página de inicio
        central_frame = QFrame()
        central_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        central_layout = QVBoxLayout(central_frame)
        
        # Logo grande
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("img/icon.png"))
        logo_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Título y subtítulo
        title = QLabel("Bienvenido a NeuroMate")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #19A7CE;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Tu asistente matemático inteligente")
        subtitle.setStyleSheet("font-size: 18px; color: #576CBC; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Descripción actualizada para incluir Montecarlo
        description = QLabel(
            "NeuroMate es una herramienta completa para realizar operaciones matemáticas "
            "avanzadas con matrices, polinomios, vectores, funciones, soluciones a ecuaciones diferenciales"
            ", vectores y valores propios, generación de números aleatorios, simulaciones de Montecarlo y sistemas de predicción. Selecciona una opción "
            "del menú lateral para comenzar."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 16px; color: #333; margin: 20px;")
        description.setAlignment(Qt.AlignCenter)
        
        # Añadir widgets al layout
        central_layout.addWidget(logo_label)
        central_layout.addWidget(title)
        central_layout.addWidget(subtitle)
        central_layout.addWidget(description)
        
        # Información de versión - actualizada por la adición de Montecarlo
        version_label = QLabel("NeuroMate v2.3")
        version_label.setStyleSheet("color: #999; font-size: 12px;")
        version_label.setAlignment(Qt.AlignRight)
        layout.addStretch(1)
        layout.addWidget(central_frame)
        layout.addStretch(1)
        layout.addWidget(version_label)
        
        return page
    
    def crear_pagina_matrices_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Título de la sección
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("img/matrices.png"))
        icon_pixmap = icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        
        title = QLabel("Operaciones con Matrices")
        title.setObjectName("title")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Mensaje de selección
        instruction_label = QLabel("Seleccione una opción del menú desplegable para comenzar")
        instruction_label.setStyleSheet("font-size: 16px; color: #333; margin: 20px; text-align: center;")
        instruction_label.setAlignment(Qt.AlignCenter)
        
        # Contenedor central para el mensaje
        central_frame = QFrame()
        central_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        central_layout = QVBoxLayout(central_frame)
        
        # Imagen de matrices
        matrix_image = QLabel()
        matrix_pixmap = QPixmap(resource_path("img/matrices.png"))
        matrix_pixmap = matrix_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        matrix_image.setPixmap(matrix_pixmap)
        matrix_image.setAlignment(Qt.AlignCenter)
        
        central_layout.addWidget(matrix_image)
        central_layout.addWidget(instruction_label)
        
        layout.addWidget(central_frame)
        layout.addStretch()
        
        return page

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        if getattr(sys, 'frozen', False):
            # Si es un .exe (PyInstaller)
            application_path = os.path.dirname(sys.executable)
            os.chdir(application_path)
        window = NeuroMate()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        error_message = f"Error crítico: {str(e)}"
        QMessageBox.critical(None, "Error en NeuroMate", error_message)
        sys.exit(1)