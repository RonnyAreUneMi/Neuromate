import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout,
    QFrame, QHBoxLayout, QLineEdit, QMessageBox, QInputDialog, QSplitter,
    QStackedWidget, QComboBox, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sympy as sp
from sympy import latex, sin, cos, tan, exp, log, pi, E
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class MathDisplay(QObject):
    mathjaxReady = pyqtSignal()
    
    @pyqtSlot()
    def notifyReady(self):
        self.mathjaxReady.emit()


class LatexRenderer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
        layout.addWidget(self.web_view)
        
        self.channel = QWebChannel()
        self.math_display = MathDisplay()
        self.channel.registerObject("mathDisplay", self.math_display)
        self.web_view.page().setWebChannel(self.channel)
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script>
                var QWebChannelMessageTypes = {
                    signal: 1,
                    propertyUpdate: 2,
                    init: 3,
                    idle: 4,
                    debug: 5,
                    invokeMethod: 6,
                    connectToSignal: 7,
                    disconnectFromSignal: 8,
                    setProperty: 9,
                    response: 10,
                };
                
                function onLoad() {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.mathDisplay = channel.objects.mathDisplay;
                        mathDisplay.notifyReady();
                    });
                }
                
                function typeset() {
                    if (window.MathJax) {
                        MathJax.typesetPromise().then(() => {
                            document.getElementById('math').style.visibility = 'visible';
                        });
                    }
                }
                
                function setLatex(latex) {
                    document.getElementById('math').innerHTML = '$$' + latex + '$$';
                    typeset();
                }
            </script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 10px;
                    background-color: white;
                    color: #000080;
                }
                #math {
                    font-size: 22px;
                    text-align: center;
                    visibility: hidden;
                    padding: 20px;
                }
                .MathJax {
                    font-size: 120% !important;
                }
            </style>
        </head>
        <body onload="onLoad()">
            <div id="math"></div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
        self.math_display.mathjaxReady.connect(self.on_mathjax_ready)
        
        self.pending_latex = None
        
    def on_mathjax_ready(self):
        if self.pending_latex:
            self.set_latex(self.pending_latex)
            
    def set_latex(self, latex_content):
        escaped_latex = latex_content.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
        script = f"setLatex('{escaped_latex}')"
        self.pending_latex = latex_content
        self.web_view.page().runJavaScript(script)


class MenuPolinomios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Calculadora de Polinomios")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(self.estilos())
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo (menú)
        self.menu_panel = QWidget()
        self.menu_panel.setObjectName("menuPanel")
        self.menu_panel.setFixedWidth(220)
        
        menu_layout = QVBoxLayout(self.menu_panel)
        menu_layout.setContentsMargins(15, 20, 15, 20)
        menu_layout.setSpacing(15)
        
        menu_line = QFrame()
        menu_line.setFrameShape(QFrame.HLine)
        menu_line.setFrameShadow(QFrame.Sunken)
        menu_line.setObjectName("menuLine")
        menu_layout.addWidget(menu_line)
        
        # Botones del menú
        menu_options = [
            ("Sumar", "sum"),
            ("Restar", "subtract"),
            ("Multiplicar", "multiply"),
            ("Derivadas", "derivative"),
            ("Integrales", "integral"),
            ("Evaluar", "evaluate")
        ]
        
        self.menu_buttons = []
        for text, action in menu_options:
            btn = QPushButton(text)
            btn.setObjectName("menuButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, act=action: self.show_operation_panel(act))
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        menu_layout.addStretch()
        
        exit_btn = QPushButton("Salir")
        exit_btn.setObjectName("exitButton")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.close)
        menu_layout.addWidget(exit_btn)
        
        # Panel derecho (contenido)
        self.content_panel = QWidget()
        self.content_panel.setObjectName("contentPanel")
        
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título principal
        self.panel_title = QLabel("📈 Calculadora de Polinomios")
        self.panel_title.setObjectName("panelTitle")
        content_layout.addWidget(self.panel_title)
        
        # Contenedor de operaciones
        self.operation_stack = QStackedWidget()
        
        # Crear paneles para cada operación
        self.create_operation_panels()
        
        content_layout.addWidget(self.operation_stack)
        
        # Añadir paneles al splitter
        self.splitter.addWidget(self.menu_panel)
        self.splitter.addWidget(self.content_panel)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        
        self.main_layout.addWidget(self.splitter)
        
        # Mostrar panel de bienvenida
        self.show_welcome_panel()
    
    def create_operation_panels(self):
        # Panel de bienvenida
        welcome_panel = QWidget()
        welcome_layout = QVBoxLayout(welcome_panel)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        welcome_msg = QLabel("Selecciona una operación del menú lateral")
        welcome_msg.setObjectName("welcomeMsg")
        welcome_layout.addWidget(welcome_msg)
        
        self.operation_stack.addWidget(welcome_panel)
        
        # Crear paneles para cada operación
        operations = ["sum", "subtract", "multiply", "derivative", "integral", "evaluate"]
        operation_names = {
            "sum": "Suma de Polinomios",
            "subtract": "Resta de Polinomios",
            "multiply": "Multiplicación de Polinomios",
            "derivative": "Derivadas",
            "integral": "Integrales",
            "evaluate": "Evaluación de Polinomios"
        }
        
        for op in operations:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setSpacing(20)
            
            # Título de operación
            op_title = QLabel(operation_names[op])
            op_title.setObjectName("operationTitle")
            layout.addWidget(op_title)
            
            # Input para polinomio A
            poly_a_layout = QVBoxLayout()
            poly_a_label = QLabel("Polinomio A:")
            poly_a_input = QLineEdit()
            
            # Configurar placeholder según la operación
            if op in ["derivative", "integral"]:
                poly_a_input.setPlaceholderText("Ejemplo: 3*x^2 + 2*x + sin(x)")
            else:
                poly_a_input.setPlaceholderText("Ejemplo: 3*x^2 + 2*x + 1")
            
            poly_a_layout.addWidget(poly_a_label)
            poly_a_layout.addWidget(poly_a_input)
            layout.addLayout(poly_a_layout)
            
            # Input para polinomio B (suma, resta y multiplicación)
            if op in ["sum", "subtract", "multiply"]:
                poly_b_layout = QVBoxLayout()
                poly_b_label = QLabel("Polinomio B:")
                poly_b_input = QLineEdit()
                poly_b_input.setPlaceholderText("Ejemplo: x^2 - x + 2")
                poly_b_layout.addWidget(poly_b_label)
                poly_b_layout.addWidget(poly_b_input)
                layout.addLayout(poly_b_layout)
                
                # Guardar referencia al input de polinomio B
                setattr(self, f"poly_b_input_{op}", poly_b_input)
            
            # Configuraciones específicas para derivadas e integrales
            if op in ["derivative", "integral"]:
                var_layout = QHBoxLayout()
                var_label = QLabel("Variable:")
                var_input = QLineEdit()
                var_input.setPlaceholderText("x")
                var_input.setText("x")
                var_input.setMaximumWidth(100)
                var_layout.addWidget(var_label)
                var_layout.addWidget(var_input)
                var_layout.addStretch()
                layout.addLayout(var_layout)
                
                # Guardar referencia al input de variable
                setattr(self, f"var_input_{op}", var_input)
                
                # Para integrales, añadir opciones adicionales
                if op == "integral":
                    integral_type_layout = QHBoxLayout()
                    integral_type_label = QLabel("Tipo de integral:")
                    integral_type_group = QButtonGroup(self)
                    
                    indefinida_radio = QRadioButton("Indefinida")
                    indefinida_radio.setChecked(True)
                    definida_radio = QRadioButton("Definida")
                    por_partes_radio = QRadioButton("Por partes")
                    
                    integral_type_group.addButton(indefinida_radio, 1)
                    integral_type_group.addButton(definida_radio, 2)
                    integral_type_group.addButton(por_partes_radio, 3)
                    
                    integral_type_layout.addWidget(integral_type_label)
                    integral_type_layout.addWidget(indefinida_radio)
                    integral_type_layout.addWidget(definida_radio)
                    integral_type_layout.addWidget(por_partes_radio)
                    integral_type_layout.addStretch()
                    layout.addLayout(integral_type_layout)
                    
                    # Límites para integrales definidas (inicialmente ocultos)
                    limits_layout = QHBoxLayout()
                    lower_limit_label = QLabel("Límite inferior:")
                    lower_limit_input = QLineEdit()
                    lower_limit_input.setPlaceholderText("a")
                    lower_limit_input.setMaximumWidth(100)
                    
                    upper_limit_label = QLabel("Límite superior:")
                    upper_limit_input = QLineEdit()
                    upper_limit_input.setPlaceholderText("b")
                    upper_limit_input.setMaximumWidth(100)
                    
                    limits_layout.addWidget(lower_limit_label)
                    limits_layout.addWidget(lower_limit_input)
                    limits_layout.addWidget(upper_limit_label)
                    limits_layout.addWidget(upper_limit_input)
                    limits_layout.addStretch()
                    layout.addLayout(limits_layout)
                    
                    # Campos para integral por partes (inicialmente ocultos)
                    parts_layout = QVBoxLayout()
                    u_label = QLabel("Función u:")
                    u_input = QLineEdit()
                    u_input.setPlaceholderText("Ejemplo: x")
                    
                    dv_label = QLabel("Función dv:")
                    dv_input = QLineEdit()
                    dv_input.setPlaceholderText("Ejemplo: e^x")
                    
                    parts_layout.addWidget(u_label)
                    parts_layout.addWidget(u_input)
                    parts_layout.addWidget(dv_label)
                    parts_layout.addWidget(dv_input)
                    layout.addLayout(parts_layout)
                    
                    # Guardar referencias
                    setattr(self, "integral_type_group", integral_type_group)
                    setattr(self, "lower_limit_input", lower_limit_input)
                    setattr(self, "upper_limit_input", upper_limit_input)
                    setattr(self, "u_input", u_input)
                    setattr(self, "dv_input", dv_input)
                    
                    # Inicialmente ocultar los campos específicos
                    lower_limit_label.setVisible(False)
                    lower_limit_input.setVisible(False)
                    upper_limit_label.setVisible(False)
                    upper_limit_input.setVisible(False)
                    u_label.setVisible(False)
                    u_input.setVisible(False)
                    dv_label.setVisible(False)
                    dv_input.setVisible(False)
                    
                    # Conectar eventos para mostrar/ocultar campos
                    definida_radio.toggled.connect(lambda checked: self.toggle_integral_fields("definida", checked))
                    por_partes_radio.toggled.connect(lambda checked: self.toggle_integral_fields("por_partes", checked))
            
            # Área de resultado
            result_label = QLabel("Resultado:")
            result_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(result_label)
            
            # Renderer para LaTeX
            latex_renderer = LatexRenderer()
            latex_renderer.setMinimumHeight(200)
            latex_renderer.set_latex("x^2 + 1")  # Expresión inicial
            layout.addWidget(latex_renderer)
            
            # Botones de acción
            btn_layout = QHBoxLayout()
            calc_btn = QPushButton("Calcular")
            calc_btn.clicked.connect(lambda checked, o=op: self.calcular(o))
            clear_btn = QPushButton("Limpiar")
            clear_btn.clicked.connect(lambda checked, o=op: self.limpiar_campos(o))
            
            btn_layout.addWidget(calc_btn)
            btn_layout.addWidget(clear_btn)
            layout.addLayout(btn_layout)
            
            # Guardar referencias a los componentes
            setattr(self, f"poly_a_input_{op}", poly_a_input)
            setattr(self, f"latex_renderer_{op}", latex_renderer)
            
            # Añadir panel al stack
            self.operation_stack.addWidget(panel)
    
    def toggle_integral_fields(self, field_type, show):
        if field_type == "definida":
            self.lower_limit_input.setVisible(show)
            self.upper_limit_input.setVisible(show)
            self.lower_limit_input.parentWidget().findChildren(QLabel)[0].setVisible(show)
            self.upper_limit_input.parentWidget().findChildren(QLabel)[1].setVisible(show)
            
            # Ocultar campos de integral por partes si se activa la definida
            if show:
                self.u_input.setVisible(False)
                self.dv_input.setVisible(False)
                self.u_input.parentWidget().findChildren(QLabel)[0].setVisible(False)
                self.dv_input.parentWidget().findChildren(QLabel)[1].setVisible(False)
                
        elif field_type == "por_partes":
            self.u_input.setVisible(show)
            self.dv_input.setVisible(show)
            self.u_input.parentWidget().findChildren(QLabel)[0].setVisible(show)
            self.dv_input.parentWidget().findChildren(QLabel)[1].setVisible(show)
            
            # Ocultar campos de integral definida si se activa por partes
            if show:
                self.lower_limit_input.setVisible(False)
                self.upper_limit_input.setVisible(False)
                self.lower_limit_input.parentWidget().findChildren(QLabel)[0].setVisible(False)
                self.upper_limit_input.parentWidget().findChildren(QLabel)[1].setVisible(False)
    
    def show_welcome_panel(self):
        self.operation_stack.setCurrentIndex(0)
        self.panel_title.setText("📈 Calculadora de Polinomios")
        
        # Quitar selección de todos los botones
        for btn in self.menu_buttons:
            btn.setProperty("selected", False)
            btn.setStyleSheet("")
    
    def show_operation_panel(self, operation):
        index = ["sum", "subtract", "multiply", "derivative", "integral", "evaluate"].index(operation) + 1
        self.operation_stack.setCurrentIndex(index)
        
        operation_names = {
            "sum": "Suma de Polinomios",
            "subtract": "Resta de Polinomios",
            "multiply": "Multiplicación de Polinomios",
            "derivative": "Derivadas",
            "integral": "Integrales",
            "evaluate": "Evaluación de Polinomios"
        }
        
        self.panel_title.setText(f"📈 {operation_names[operation]}")
        
        # Actualizar estilo de botones del menú
        for i, btn in enumerate(self.menu_buttons):
            if i == index - 1:
                btn.setProperty("selected", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            else:
                btn.setProperty("selected", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
    
    def calcular(self, operation):
        try:
            poly_a_input = getattr(self, f"poly_a_input_{operation}")
            polinomio_a = poly_a_input.text().strip()
            latex_renderer = getattr(self, f"latex_renderer_{operation}")
            
            if operation in ["sum", "subtract", "multiply"]:
                poly_b_input = getattr(self, f"poly_b_input_{operation}")
                polinomio_b = poly_b_input.text().strip()
                
                if not polinomio_a or not polinomio_b:
                    QMessageBox.warning(self, "Campos vacíos", "Debes completar ambos polinomios.")
                    return
            else:
                polinomio_b = ""
                if not polinomio_a:
                    QMessageBox.warning(self, "Campo vacío", "Debes ingresar al menos el Polinomio A.")
                    return

            # Obtener la variable para derivar/integrar (por defecto 'x')
            variable = 'x'
            if operation in ["derivative", "integral"]:
                var_input = getattr(self, f"var_input_{operation}")
                variable_input = var_input.text().strip()
                if variable_input:
                    variable = variable_input

            # Crear el símbolo para la variable
            x = sp.Symbol(variable)
            
            # Preprocesar las entradas
            polinomio_a = self.preprocesar_expresion(polinomio_a, variable)
            if polinomio_b:
                polinomio_b = self.preprocesar_expresion(polinomio_b, variable)
            
            # Convertir strings a expresiones sympy
            expr_a = self.convertir_a_sympy(polinomio_a, x)
            
            if operation in ["sum", "subtract", "multiply"]:
                expr_b = self.convertir_a_sympy(polinomio_b, x)
                
                if operation == "sum":
                    resultado = expr_a + expr_b
                    operacion_latex = f"{latex(expr_a)} + {latex(expr_b)} = {latex(resultado)}"
                elif operation == "subtract":
                    resultado = expr_a - expr_b
                    operacion_latex = f"{latex(expr_a)} - {latex(expr_b)} = {latex(resultado)}"
                elif operation == "multiply":
                    resultado = expr_a * expr_b
                    operacion_latex = f"{latex(expr_a)} \\cdot {latex(expr_b)} = {latex(resultado)}"
            
            elif operation == "derivative":
                resultado = sp.diff(expr_a, x)
                operacion_latex = f"\\frac{{d}}{{d{variable}}}({latex(expr_a)}) = {latex(resultado)}"
            
            elif operation == "integral":
                # Determinar el tipo de integral seleccionado
                integral_type = self.integral_type_group.checkedId()
                
                if integral_type == 1:  # Indefinida
                    resultado = sp.integrate(expr_a, x)
                    operacion_latex = f"\\int {latex(expr_a)} \\, d{variable} = {latex(resultado)} + C"
                
                elif integral_type == 2:  # Definida
                    lower = self.lower_limit_input.text().strip()
                    upper = self.upper_limit_input.text().strip()
                    
                    if not lower or not upper:
                        QMessageBox.warning(self, "Límites faltantes", "Debes especificar ambos límites para la integral definida.")
                        return
                    
                    try:
                        lower_val = self.convertir_a_sympy(lower, x)
                        upper_val = self.convertir_a_sympy(upper, x)
                        
                        resultado = sp.integrate(expr_a, (x, lower_val, upper_val))
                        operacion_latex = f"\\int_{{{latex(lower_val)}}}^{{{latex(upper_val)}}} {latex(expr_a)} \\, d{variable} = {latex(resultado)}"
                    except Exception as e:
                        QMessageBox.critical(self, "Error en límites", f"Error al procesar los límites: {str(e)}")
                        return
                
                elif integral_type == 3:  # Por partes
                    u_expr = self.u_input.text().strip()
                    dv_expr = self.dv_input.text().strip()
                    
                    if not u_expr or not dv_expr:
                        QMessageBox.warning(self, "Funciones faltantes", "Debes especificar ambas funciones u y dv para la integral por partes.")
                        return
                    
                    try:
                        u = self.convertir_a_sympy(u_expr, x)
                        dv = self.convertir_a_sympy(dv_expr, x)
                        
                        # Calcular du/dx
                        du = sp.diff(u, x)
                        
                        # Calcular v (integral de dv)
                        v = sp.integrate(dv, x)
                        
                        # Aplicar fórmula de integración por partes: ∫u·dv = u·v - ∫v·du
                        resultado = u * v - sp.integrate(v * du, x)
                        
                        operacion_latex = f"\\int {latex(u)} \\cdot {latex(dv)} \\, d{variable} = {latex(u)} \\cdot {latex(v)} - \\int {latex(v)} \\cdot {latex(du)} \\, d{variable} = {latex(resultado)} + C"
                    except Exception as e:
                        QMessageBox.critical(self, "Error en las funciones", f"Error al procesar las funciones para integral por partes: {str(e)}")
                        return
            
            elif operation == "evaluate":
                valor, ok = QInputDialog.getDouble(self, "Evaluar", f"Ingresa el valor de {variable}:")
                if ok:
                    resultado = expr_a.subs(x, valor)
                    operacion_latex = f"{latex(expr_a)}\\,|_{{{variable}={valor}}} = {latex(resultado)}"
                else:
                    return

            # Mostrar resultado
            latex_renderer.set_latex(operacion_latex)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            latex_renderer.set_latex("\\text{Error en la operación}")

    def preprocesar_expresion(self, expr_str, var='x'):
        expr_str = expr_str.replace("sen", "sin")
        expr_str = expr_str.replace("tg", "tan")
        expr_str = expr_str.replace("^", "**")
        
        trig_funcs = ["sin", "cos", "tan", "cot", "sec", "csc", 
                     "asin", "acos", "atan", "asinh", "acosh", "atanh"]
        
        for func in trig_funcs:
            pattern = r'{}([a-zA-Z0-9])'.format(func)
            expr_str = re.sub(pattern, r'{}(\1)'.format(func), expr_str)
            
            pattern = r'{}\s+([a-zA-Z0-9])'.format(func)
            expr_str = re.sub(pattern, r'{}(\1)'.format(func), expr_str)
        
        expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
        expr_str = re.sub(r'\)(\()', r')*\1', expr_str)
        expr_str = re.sub(r'e\*\*\(([^)]+)\)', r'exp(\1)', expr_str)
        
        return expr_str

    def convertir_a_sympy(self, expr_str, x):
        local_dict = {
            variable: sp.Symbol(variable) for variable in "abcdefghijklmnopqrstuvwxyz"
        }
        
        local_dict.update({
            'x': x,
            'pi': sp.pi,
            'e': sp.E,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'cot': sp.cot,
            'sec': sp.sec,
            'csc': sp.csc,
            'asin': sp.asin,
            'acos': sp.acos,
            'atan': sp.atan,
            'sinh': sp.sinh,
            'cosh': sp.cosh,
            'tanh': sp.tanh,
            'exp': sp.exp,
            'log': sp.log,
            'ln': sp.log,
            'sqrt': sp.sqrt,
        })
        
        try:
            return sp.sympify(expr_str, locals=local_dict)
        except Exception as e:
            if "parenthesis" in str(e).lower():
                raise ValueError("Error de paréntesis no balanceados")
            elif "invalid syntax" in str(e).lower():
                raise ValueError(f"Error de sintaxis en la expresión. Verifica que las funciones trigonométricas tengan paréntesis.")
            else:
                raise ValueError(f"Error al procesar la expresión: {str(e)}")

    def limpiar_campos(self, operation):
        poly_a_input = getattr(self, f"poly_a_input_{operation}")
        poly_a_input.clear()
        
        if operation in ["sum", "subtract", "multiply"]:
            poly_b_input = getattr(self, f"poly_b_input_{operation}")
            poly_b_input.clear()
            
        if operation in ["derivative", "integral"]:
            var_input = getattr(self, f"var_input_{operation}")
            var_input.setText("x")
            
            if operation == "integral":
                # Reiniciar campos de integración
                self.lower_limit_input.clear()
                self.upper_limit_input.clear()
                self.u_input.clear()
                self.dv_input.clear()
                
                # Seleccionar integración indefinida por defecto
                self.integral_type_group.button(1).setChecked(True)
            
        latex_renderer = getattr(self, f"latex_renderer_{operation}")
        latex_renderer.set_latex("x^2 + 1")

    def estilos(self):
        return """
        QWidget {
            background-color: #ffffff;
            color: #000000;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
        }
        
        QWidget#menuPanel {
            background-color: #000080;
            border-right: 1px solid #000066;
        }
        
        QLabel#appTitle {
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            padding-bottom: 10px;
        }
        
        QFrame#menuLine {
            color: #3355aa;
            background-color: #3355aa;
        }
        
        QPushButton#menuButton {
            background-color: transparent;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 10px;
            text-align: left;
            font-size: 16px;
            font-weight: bold;
        }
        
        QPushButton#menuButton:hover {
            background-color: #0000b3;
        }
        
        QPushButton#menuButton[selected="true"] {
            background-color: #0000cc;
            border-left: 4px solid #ffffff;
        }
        
        QPushButton#exitButton {
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }
        
        QPushButton#exitButton:hover {
            background-color: #cc0000;
        }
        
        QLabel#panelTitle {
            font-size: 24px;
            font-weight: bold;
            color: #000080;
            padding-bottom: 20px;
            border-bottom: 2px solid #000080;
        }
        
        QLabel#operationTitle {
            font-size: 20px;
            font-weight: bold;
            color: #000080;
        }
        
        QLabel#welcomeMsg {
            font-size: 22px;
            color: #666666;
        }
        
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #000080;
            border-radius: 5px;
            padding: 8px;
            font-size: 16px;
        }
        
        QPushButton {
            background-color: #000080;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 15px;
        }
        
        QPushButton:hover {
            background-color: #0000b3;
        }
        
        QRadioButton {
            font-size: 14px;
            color: #000080;
        }
        
        QRadioButton::indicator {
            width: 15px;
            height: 15px;
        }
        """