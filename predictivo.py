import numpy as np
from scipy.integrate import odeint
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, 
                             QGridLayout, QMessageBox, QFileDialog, QCheckBox, QComboBox, 
                             QSlider, QGroupBox, QSpinBox, QDoubleSpinBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class Prediccion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modelo SEIR Avanzado de Propagación de Epidemias")
        self.setStyleSheet("background-color: #F5F8FA; color: #333333; font-family: 'Helvetica Neue', sans-serif;")
        self.setGeometry(100, 100, 1200, 800)  # Ajustar tamaño para mantener proporciones originales

        # Valores predeterminados del modelo epidemiológico
        self.configuracion_default = {
            'poblacion_total': 100000,
            'expuestos_iniciales': 10,
            'infectados_iniciales': 5,
            'tasa_transmision': 0.35,
            'tasa_incubacion': 0.2,
            'tasa_recuperacion': 0.1,
            'tasa_mortalidad': 0.01,
            'tasa_natalidad': 0.001,
            'dias_simulacion': 200,
            'efectividad_vacuna': 0.75,
            'cobertura_vacunacion': 0.5
        }

        # Definir compartimentos y colores
        self.compartimentos = {
            'Susceptibles': {'color': 'blue', 'visible': True},
            'Expuestos': {'color': 'orange', 'visible': True},
            'Infectados': {'color': 'red', 'visible': True},
            'Recuperados': {'color': 'green', 'visible': True},
            'Fallecidos': {'color': 'black', 'visible': True}
        }
        
        # Almacenar resultados de la simulación
        self.resultados_simulacion = None
        self.tiempo_simulacion = None

        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        main_layout = QHBoxLayout(self)
        panel_izquierdo = QVBoxLayout()

        # Título y descripción
        self.crear_encabezado(panel_izquierdo)

        # Sección de parámetros
        self.crear_grupo_parametros(panel_izquierdo)

        # Sección de intervenciones
        self.crear_grupo_intervenciones(panel_izquierdo)

        # Sección de estadísticas
        self.crear_grupo_estadisticas(panel_izquierdo)

        # Botones de acción
        self.crear_botones(panel_izquierdo)
        
        # Panel derecho para gráfico y selector de líneas
        panel_derecho = QVBoxLayout()
        
        # Selector de líneas
        self.crear_selector_lineas(panel_derecho)

        # Configuración del gráfico
        self.figura = Figure(figsize=(8, 6), facecolor='white', dpi=100)
        self.canvas = FigureCanvas(self.figura)
        panel_derecho.addWidget(self.canvas)
        
        main_layout.addLayout(panel_izquierdo, 1)
        main_layout.addLayout(panel_derecho, 2)

        self.inicializar_figura()

    def crear_encabezado(self, panel_izquierdo):
        titulo = QLabel("🦠 Modelo SEIR Epidemiológico Avanzado")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2D3E50; margin-bottom: 20px;")
        panel_izquierdo.addWidget(titulo)

        descripcion = QLabel(
            "Simulación epidemiológica avanzada considerando exposición, vacunación "
            "y estrategias de mitigación de riesgo.")
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("font-size: 14px; margin-bottom: 20px; text-align: center;")
        panel_izquierdo.addWidget(descripcion)

    def crear_grupo_parametros(self, panel_izquierdo):
        grupo_parametros = QGroupBox("Parámetros Epidemiológicos")
        grupo_parametros.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #B0D2E0; border-radius: 8px; margin-top: 10px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }"
        )
        layout_parametros = QGridLayout()

        parametros = [
            ("Población Total", "poblacion_total", 1000, 10000000, QSpinBox),
            ("Expuestos Iniciales", "expuestos_iniciales", 0, 1000, QSpinBox),
            ("Infectados Iniciales", "infectados_iniciales", 0, 1000, QSpinBox),
            ("Tasa de Transmisión (β)", "tasa_transmision", 0.01, 1.0, QDoubleSpinBox),
            ("Tasa de Incubación (σ)", "tasa_incubacion", 0.01, 1.0, QDoubleSpinBox),
            ("Tasa de Recuperación (γ)", "tasa_recuperacion", 0.01, 1.0, QDoubleSpinBox),
            ("Tasa de Mortalidad (α)", "tasa_mortalidad", 0.001, 0.1, QDoubleSpinBox),
            ("Tasa de Natalidad (ν)", "tasa_natalidad", 0.0001, 0.01, QDoubleSpinBox),
            ("Días de Simulación", "dias_simulacion", 30, 365, QSpinBox)
        ]

        self.controles_parametros = {}
        for i, (etiqueta, atributo, minimo, maximo, tipo_control) in enumerate(parametros):
            control = tipo_control()
            control.setRange(minimo, maximo)
            control.setValue(self.configuracion_default[atributo])
            control.setSingleStep(0.01 if tipo_control == QDoubleSpinBox else 1)
            
            layout_parametros.addWidget(QLabel(etiqueta), i, 0)
            layout_parametros.addWidget(control, i, 1)
            
            self.controles_parametros[atributo] = control

        grupo_parametros.setLayout(layout_parametros)
        panel_izquierdo.addWidget(grupo_parametros)

    def crear_grupo_intervenciones(self, panel_izquierdo):
        grupo_intervenciones = QGroupBox("Intervenciones Epidemiológicas")
        grupo_intervenciones.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #B0D2E0; border-radius: 8px; margin-top: 10px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }"
        )
        layout_intervenciones = QGridLayout()

        # Vacunación
        self.check_vacunacion = QCheckBox("Implementar Vacunación")
        self.check_vacunacion.setChecked(False)
        layout_intervenciones.addWidget(self.check_vacunacion, 0, 0, 1, 2)

        layout_intervenciones.addWidget(QLabel("Efectividad de Vacuna:"), 1, 0)
        self.spin_efectividad_vacuna = QDoubleSpinBox()
        self.spin_efectividad_vacuna.setRange(0.0, 1.0)
        self.spin_efectividad_vacuna.setValue(self.configuracion_default['efectividad_vacuna'])
        self.spin_efectividad_vacuna.setSingleStep(0.05)
        layout_intervenciones.addWidget(self.spin_efectividad_vacuna, 1, 1)

        layout_intervenciones.addWidget(QLabel("Cobertura de Vacunación:"), 2, 0)
        self.spin_cobertura_vacunacion = QDoubleSpinBox()
        self.spin_cobertura_vacunacion.setRange(0.0, 1.0)
        self.spin_cobertura_vacunacion.setValue(self.configuracion_default['cobertura_vacunacion'])
        self.spin_cobertura_vacunacion.setSingleStep(0.05)
        layout_intervenciones.addWidget(self.spin_cobertura_vacunacion, 2, 1)

        grupo_intervenciones.setLayout(layout_intervenciones)
        panel_izquierdo.addWidget(grupo_intervenciones)

    def crear_grupo_estadisticas(self, panel_izquierdo):
        grupo_estadisticas = QGroupBox("Métricas Epidemiológicas")
        grupo_estadisticas.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #B0D2E0; border-radius: 8px; margin-top: 10px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }"
        )
        layout_estadisticas = QVBoxLayout()

        self.label_r0 = QLabel("Número Reproductivo Básico (R₀): --")
        self.label_pico_infectados = QLabel("Pico de Infectados: --")
        self.label_total_infectados = QLabel("Total de Casos: --")
        self.label_letalidad = QLabel("Tasa de Letalidad: --")

        for label in [self.label_r0, self.label_pico_infectados, 
                      self.label_total_infectados, self.label_letalidad]:
            label.setStyleSheet("font-size: 14px; margin: 5px 0;")
            layout_estadisticas.addWidget(label)

        grupo_estadisticas.setLayout(layout_estadisticas)
        panel_izquierdo.addWidget(grupo_estadisticas)

    def crear_selector_lineas(self, panel_derecho):
        grupo_selector = QGroupBox("Selección de Visualización")
        grupo_selector.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #B0D2E0; border-radius: 8px; margin-bottom: 10px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }"
        )
        
        layout_selector = QHBoxLayout()
        layout_selector.setSpacing(5)  # Espacio reducido entre botones
        
        # Botones para cada compartimento (solo colores sin texto)
        self.botones_compartimentos = {}
        for nombre, datos in self.compartimentos.items():
            color = datos['color']
            
            # Crear un botón cuadrado pequeño sin texto
            boton = QPushButton()
            boton.setFixedSize(20, 20)  # Tamaño reducido
            boton.setCheckable(True)
            boton.setChecked(True)
            boton.setToolTip(nombre)  # Mostrar nombre al pasar el mouse
            
            # Estilo para mostrar solo el color
            boton.setStyleSheet(
                f"QPushButton {{ background-color: {color}; border-radius: 3px; }}"
                f"QPushButton:checked {{ background-color: {color}; border: 2px solid white; }}"
                f"QPushButton:!checked {{ background-color: #888888; }}"
            )
            
            # Conectar con la función que actualiza la visualización
            boton.toggled.connect(lambda checked, btn=nombre: self.actualizar_visibilidad(btn, checked))
            
            layout_selector.addWidget(boton)
            self.botones_compartimentos[nombre] = boton
        
        # Botón para mostrar/ocultar todos (más pequeño)
        boton_todos = QPushButton("⟲")  # Símbolo de refrescar para ahorrar espacio
        boton_todos.setFixedSize(20, 20)
        boton_todos.setToolTip("Mostrar/Ocultar Todos")
        boton_todos.setStyleSheet(
            "QPushButton { background-color: #2D3E50; color: white; border-radius: 3px; }"
        )
        boton_todos.clicked.connect(self.alternar_todos)
        layout_selector.addWidget(boton_todos)
        
        # Agregar espacio expandible al final para mantener los botones juntos a la izquierda
        layout_selector.addStretch(1)
        
        grupo_selector.setLayout(layout_selector)
        panel_derecho.addWidget(grupo_selector)

    def crear_botones(self, panel_izquierdo):
        botones_layout = QHBoxLayout()
        
        botones = [
            ("🧬 Simular", self.simular_modelo, "background-color: #007BFF;"),
            ("💾 Guardar Resultados", self.guardar_imagen, "background-color: #28a745;"),
            ("🔄 Restablecer", self.restablecer_valores, "background-color: #dc3545;")
        ]

        for texto, funcion, estilo in botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(f"{estilo} color: white; font-weight: bold; border-radius: 8px; padding: 10px;")
            boton.clicked.connect(funcion)
            botones_layout.addWidget(boton)

        panel_izquierdo.addLayout(botones_layout)

    def actualizar_visibilidad(self, compartimento, visible):
        """Actualiza la visibilidad de una línea en la gráfica"""
        self.compartimentos[compartimento]['visible'] = visible
        
        # Si tenemos resultados, actualizamos la gráfica
        if self.resultados_simulacion is not None:
            self.actualizar_grafica()

    def alternar_todos(self):
        """Alterna la visibilidad de todas las líneas"""
        # Verificar si todos están visibles o no
        todos_visibles = all(datos['visible'] for datos in self.compartimentos.values())
        
        # Alternar estado
        nuevo_estado = not todos_visibles
        
        # Actualizar todos los botones y estados
        for nombre, boton in self.botones_compartimentos.items():
            boton.setChecked(nuevo_estado)
            self.compartimentos[nombre]['visible'] = nuevo_estado
        
        # Actualizar gráfica si hay resultados
        if self.resultados_simulacion is not None:
            self.actualizar_grafica()

    def modelo_seir(self, y, t, N, beta, sigma, gamma, alpha, nu, 
                    vacunacion_activa, efectividad_vacuna, cobertura_vacunacion):
        S, E, I, R, D = y
        
        # Flujos entre compartimentos
        dSdt = nu * N - beta * S * I / N - S * vacunacion_activa * cobertura_vacunacion
        dEdt = beta * S * I / N - (sigma + alpha) * E
        dIdt = sigma * E - (gamma + alpha) * I
        dRdt = gamma * I + efectividad_vacuna * S * vacunacion_activa * cobertura_vacunacion
        dDdt = alpha * (E + I)

        return [dSdt, dEdt, dIdt, dRdt, dDdt]

    def calcular_r0(self, beta, sigma, gamma, alpha):
        return (beta * sigma) / ((sigma + alpha) * (gamma + alpha))

    def simular_modelo(self):
        # Obtener parámetros de la interfaz
        N = self.controles_parametros['poblacion_total'].value()
        E0 = self.controles_parametros['expuestos_iniciales'].value()
        I0 = self.controles_parametros['infectados_iniciales'].value()
        
        beta = self.controles_parametros['tasa_transmision'].value()
        sigma = self.controles_parametros['tasa_incubacion'].value()
        gamma = self.controles_parametros['tasa_recuperacion'].value()
        alpha = self.controles_parametros['tasa_mortalidad'].value()
        nu = self.controles_parametros['tasa_natalidad'].value()
        dias = self.controles_parametros['dias_simulacion'].value()

        # Condiciones iniciales
        S0 = N - E0 - I0
        R0 = 0
        D0 = 0
        y0 = [S0, E0, I0, R0, D0]

        # Tiempo de simulación
        self.tiempo_simulacion = np.linspace(0, dias, dias + 1)

        # Parámetros de vacunación
        vacunacion_activa = 1 if self.check_vacunacion.isChecked() else 0
        efectividad_vacuna = self.spin_efectividad_vacuna.value()
        cobertura_vacunacion = self.spin_cobertura_vacunacion.value()

        # Resolver modelo
        self.resultados_simulacion = odeint(
            self.modelo_seir, 
            y0, 
            self.tiempo_simulacion, 
            args=(
                N, beta, sigma, gamma, alpha, nu, 
                vacunacion_activa, efectividad_vacuna, cobertura_vacunacion
            )
        )

        S, E, I, R, D = self.resultados_simulacion.T

        # Calcular métricas
        r0 = self.calcular_r0(beta, sigma, gamma, alpha)
        pico_infectados = max(I)
        dia_pico = np.argmax(I)
        total_infectados = N - S[-1]
        letalidad = D[-1] / total_infectados if total_infectados > 0 else 0

        # Actualizar etiquetas
        self.label_r0.setText(f"R₀: {r0:.2f}")
        self.label_pico_infectados.setText(f"Pico de Infectados: {int(pico_infectados)} (Día {dia_pico})")
        self.label_total_infectados.setText(f"Total de Casos: {int(total_infectados)}")
        self.label_letalidad.setText(f"Tasa de Letalidad: {letalidad*100:.2f}%")

        # Graficar resultados
        self.actualizar_grafica()

    def actualizar_grafica(self):
        """Actualiza la gráfica según la visibilidad de las líneas"""
        # Asegurarse de que haya resultados
        if self.resultados_simulacion is None:
            return
            
        S, E, I, R, D = self.resultados_simulacion.T
        t = self.tiempo_simulacion
        
        # Nombres y datos de los compartimentos
        nombres_compartimentos = ['Susceptibles', 'Expuestos', 'Infectados', 'Recuperados', 'Fallecidos']
        datos_compartimentos = [S, E, I, R, D]
        
        # Limpiar figura
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        
        # Dibujar solo las líneas visibles
        for nombre, datos in zip(nombres_compartimentos, datos_compartimentos):
            if self.compartimentos[nombre]['visible']:
                ax.plot(t, datos, label=nombre, color=self.compartimentos[nombre]['color'], linewidth=2.5)
        
        # Calcular R0 para el título
        beta = self.controles_parametros['tasa_transmision'].value()
        sigma = self.controles_parametros['tasa_incubacion'].value()
        gamma = self.controles_parametros['tasa_recuperacion'].value()
        alpha = self.controles_parametros['tasa_mortalidad'].value()
        r0 = self.calcular_r0(beta, sigma, gamma, alpha)
        
        # Añadir etiquetas y leyenda
        ax.set_title(f'Modelo SEIR - R₀: {r0:.2f}')
        ax.set_xlabel('Días')
        ax.set_ylabel('Población')
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ajustar márgenes para mejor visualización
        self.figura.tight_layout()
        
        self.canvas.draw()

    def guardar_imagen(self):
        """Guarda la gráfica actual como imagen"""
        if self.resultados_simulacion is None:
            QMessageBox.warning(self, "Sin Resultados", "Primero debes realizar una simulación.")
            return
            
        opciones = QFileDialog.Options()
        nombre_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar Gráfica", "modelo_seir_epidemia", 
            "Imágenes PNG (*.png);;Imágenes JPG (*.jpg);;Todos los archivos (*)",
            options=opciones)
            
        if nombre_archivo:
            try:
                # Asegurar extensión
                if not (nombre_archivo.endswith('.png') or nombre_archivo.endswith('.jpg')):
                    nombre_archivo += '.png'
                
                self.figura.savefig(nombre_archivo, dpi=200, bbox_inches='tight')
                QMessageBox.information(self, "Guardado Exitoso", 
                                      f"La gráfica se ha guardado como {nombre_archivo}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Guardado", 
                                   f"No se pudo guardar la imagen: {str(e)}")

    def restablecer_valores(self):
        """Restablece todos los parámetros a sus valores predeterminados"""
        # Restaurar controles de parámetros
        for atributo, control in self.controles_parametros.items():
            control.setValue(self.configuracion_default[atributo])
        
        # Desactivar vacunación
        self.check_vacunacion.setChecked(False)
        self.spin_efectividad_vacuna.setValue(self.configuracion_default['efectividad_vacuna'])
        self.spin_cobertura_vacunacion.setValue(self.configuracion_default['cobertura_vacunacion'])
        
        # Limpiar estadísticas
        self.label_r0.setText("Número Reproductivo Básico (R₀): --")
        self.label_pico_infectados.setText("Pico de Infectados: --")
        self.label_total_infectados.setText("Total de Casos: --")
        self.label_letalidad.setText("Tasa de Letalidad: --")
        
        # Restablecer visibilidad de líneas
        for nombre in self.compartimentos:
            self.compartimentos[nombre]['visible'] = True
            if nombre in self.botones_compartimentos:
                self.botones_compartimentos[nombre].setChecked(True)
                
        # Reiniciar datos de simulación
        self.resultados_simulacion = None
        self.tiempo_simulacion = None
        
        # Reiniciar figura
        self.inicializar_figura()

    def inicializar_figura(self):
        """Inicializa la figura con un mensaje de bienvenida"""
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.text(0.5, 0.5, "Presiona 'Simular' para iniciar la simulación epidemiológica", 
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_axis_off()
        self.canvas.draw()