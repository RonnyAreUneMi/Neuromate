import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QFrame, QGroupBox, QHeaderView,
    QComboBox, QFormLayout, QDoubleSpinBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')
plt.style.use('seaborn-v0_8-whitegrid')


class RandomGenerator:
    """Clase que implementa diferentes algoritmos de generación de números aleatorios"""
    
    @staticmethod
    def mersenne_twister(n, seed=None):
        """Generador Mersenne Twister usando numpy"""
        # Usamos numpy que ya implementa Mersenne Twister
        np.random.seed(seed)  # Usa la semilla proporcionada
        return list(np.random.random(n))
    
    @staticmethod
    def xorshift(n, seed=123456789):
        """Implementación básica de XorShift"""
        numbers = []
        state = seed
        for _ in range(n):
            # XorShift algorithm (32-bit)
            state ^= (state << 13) & 0xFFFFFFFF
            state ^= (state >> 17) & 0xFFFFFFFF
            state ^= (state << 5) & 0xFFFFFFFF
            # Normalizar a [0,1)
            numbers.append(state / 0xFFFFFFFF)
        return numbers
    
    @staticmethod
    def pcg(n, seed=42, mult=6364136223846793005, inc=1442695040888963407):
        """Implementación básica de PCG (Permuted Congruential Generator)"""
        numbers = []
        state = seed
        for _ in range(n):
            # Actualizar estado usando LCG
            state = (mult * state + inc) & 0xFFFFFFFFFFFFFFFF
            # Aplicar función de salida PCG
            xorshifted = (((state >> 18) ^ state) >> 27) & 0xFFFFFFFF
            rot = state >> 59
            result = ((xorshifted >> rot) | (xorshifted << (32 - rot))) & 0xFFFFFFFF
            # Normalizar a [0,1)
            numbers.append(result / 0xFFFFFFFF)
        return numbers
    
    @staticmethod
    def well(n, seed=123456789):
        """Implementación simplificada de WELL (Well Equidistributed Long-period Linear)"""
        # Usamos numpy.random.random() como aproximación, ya que una implementación
        # completa de WELL es bastante compleja
        np.random.seed(seed)
        return list(np.random.random(n))
    
    @staticmethod
    def lcg(n, seed=123456789, a=1103515245, c=12345, m=2**31):
        """Generador Congruencial Lineal Mixto"""
        numbers = []
        x = seed
        for _ in range(n):
            x = (a * x + c) % m
            numbers.append(x / m)
        return numbers
    
    @staticmethod
    def mcg(n, seed=123456789, a=48271, m=2**31-1):
        """Generador Congruencial Multiplicativo"""
        numbers = []
        x = seed
        for _ in range(n):
            x = (a * x) % m
            numbers.append(x / m)
        return numbers
    
    @staticmethod
    def tausworthe(n, seed=123456789):
        """Implementación básica de generador Tausworthe/LFSR"""
        numbers = []
        r = 32  # Tamaño del registro
        q = 3  # Posición de tap
        s = seed
        for _ in range(n):
            result = 0
            for j in range(32):
                bit = (s >> 0) & 1  # Bit menos significativo
                result = result | (bit << j)
                new_bit = ((s >> 0) ^ (s >> q)) & 1  # XOR de bits en posiciones 0 y q
                s = (s >> 1) | (new_bit << (r-1))  # Desplazar y añadir nuevo bit
            # Normalizar a [0,1)
            numbers.append(result / 0xFFFFFFFF)
        return numbers
    
    @staticmethod
    def middle_square(n, seed=675248):
        """Método de Productos Medios (Von Neumann)"""
        numbers = []
        digits = len(str(seed))
        if digits % 2 != 0:
            seed = seed * 10  # Asegurar un número par de dígitos
            digits += 1
        
        x = seed
        for _ in range(n):
            x_squared = x * x
            x_squared_str = str(x_squared).zfill(digits * 2)
            
            # Extraer dígitos del medio
            start = (len(x_squared_str) - digits) // 2
            x = int(x_squared_str[start:start+digits])
            
            # Normalizar a [0,1)
            numbers.append(x / (10**digits))
            
            # Verificar si hemos llegado a un ciclo (prevenir bucles)
            if x == 0:
                x = seed
        
        return numbers
    
    @staticmethod
    def middle_square_weyl(n, seed=675248, w_seed=123456789):
        """Método Cuadrático Medio con la secuencia de Weyl para evitar ciclos"""
        numbers = []
        x = seed
        w = w_seed
        m = 2**32
        
        for _ in range(n):
            # Actualizar secuencia de Weyl
            w = (w + w_seed) % m
            
            # Combinar con el estado actual
            x = (x + w) % m
            
            # Operación cuadrado medio
            y = (x * x) % m
            
            # Normalizar a [0,1)
            numbers.append(y / m)
            
            # Actualizar x para la siguiente iteración
            x = y
        
        return numbers
class DistributionTransformer:
    """Clase para transformar números aleatorios uniformes a otras distribuciones"""
    
    @staticmethod
    def uniform(random_nums, a=0, b=1):
        """Distribución Uniforme en [a,b]"""
        return [a + (b - a) * r for r in random_nums]
    
    @staticmethod
    def normal(random_nums, mean=0, std=1):
        """Distribución Normal (Box-Muller)"""
        result = []
        # Asegurar que tenemos un número par de valores
        if len(random_nums) % 2 != 0:
            random_nums = random_nums[:-1]
        
        for i in range(0, len(random_nums), 2):
            if i+1 < len(random_nums):
                u1 = random_nums[i]
                u2 = random_nums[i+1]
                
                # Evitar logaritmo de cero
                if u1 <= 0:
                    u1 = 0.0001
                
                # Transformación Box-Muller
                z1 = mean + std * np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
                z2 = mean + std * np.sqrt(-2 * np.log(u1)) * np.sin(2 * np.pi * u2)
                
                result.append(z1)
                result.append(z2)
        
        # Asegurar que devolvemos exactamente la cantidad solicitada
        return result[:len(random_nums)]
    
    @staticmethod
    def exponential(random_nums, lambd=1.0):
        """Distribución Exponencial"""
        # Transformación inversa
        return [-np.log(1 - r) / lambd for r in random_nums]
    
    @staticmethod
    def poisson(random_nums, lambd=1.0):
        """Distribución de Poisson - Algoritmo de transformación por rechazo"""
        result = []
        
        for r in random_nums:
            # Algoritmo directo para generar Poisson
            L = np.exp(-lambd)
            k = 0
            p = 1
            
            while p > L:
                k += 1
                # Generar otro número aleatorio - usando numpy aquí para simplificar
                u = np.random.random()
                p *= u
            
            result.append(k-1)
        
        return result
    
    @staticmethod
    def binomial(random_nums, n=10, p=0.5):
        """Distribución Binomial - suma de n ensayos de Bernoulli"""
        result = []
        
        for i in range(0, len(random_nums), n):
            # Tomar n valores o lo que quede si no hay suficientes
            subset = random_nums[i:i+n]
            if len(subset) < n:
                # Si no hay suficientes valores, repetir algunos
                subset = subset + subset[:n-len(subset)]
            
            # Contar éxitos (r <= p)
            successes = sum(1 for r in subset if r <= p)
            result.append(successes)
        
        # Puede que generemos menos resultados que la entrada original
        # Repetir resultados si es necesario
        while len(result) < len(random_nums):
            result.append(result[len(result) % len(result)])
        
        return result[:len(random_nums)]
    
    @staticmethod
    def gamma(random_nums, shape=1.0, scale=1.0):
        """Distribución Gamma - Implementación simplificada"""
        result = []
        
        for r in random_nums:
            # Para shape >= 1, usamos aproximación
            if shape >= 1:
                # Usar la transformación básica - en la práctica se utilizaría
                # un algoritmo más sofisticado como Marsaglia-Tsang
                u = np.random.random()  # Otro número aleatorio
                x = -np.log(r * u) * scale
                result.append(x)
            else:
                # Para shape < 1 también necesitaríamos otro algoritmo
                # Esta es una aproximación muy básica
                x = -np.log(r) * scale
                result.append(x)
        
        return result
    
    @staticmethod
    def beta(random_nums, alpha=2.0, beta=2.0):
        """Distribución Beta"""
        result = []
        
        # Necesitamos pares de números aleatorios
        if len(random_nums) % 2 != 0:
            random_nums = random_nums[:-1]
        
        for i in range(0, len(random_nums), 2):
            if i+1 < len(random_nums):
                u1 = random_nums[i]
                u2 = random_nums[i+1]
                
                # Evitar logaritmo de cero
                if u1 <= 0:
                    u1 = 0.0001
                if u2 <= 0:
                    u2 = 0.0001
                
                # Usar aproximación - en la práctica se utilizaría otro algoritmo
                y1 = u1 ** (1/alpha)
                y2 = u2 ** (1/beta)
                
                if y1 + y2 <= 1:
                    x = y1 / (y1 + y2)
                    result.append(x)
                else:
                    # Si no cumple la condición, generar otro número
                    result.append(np.random.beta(alpha, beta))
        
        # Asegurar que devolvemos exactamente la cantidad solicitada
        while len(result) < len(random_nums):
            result.append(np.random.beta(alpha, beta))
        
        return result[:len(random_nums)]
    
    @staticmethod
    def chi_squared(random_nums, df=1):
        """Distribución Chi-cuadrado (caso especial de Gamma)"""
        # Chi-cuadrado es un caso especial de Gamma con shape=df/2 y scale=2
        return DistributionTransformer.gamma(random_nums, shape=df/2, scale=2)
    
    @staticmethod
    def t_distribution(random_nums, df=1):
        """Distribución t-Student"""
        result = []
        
        # Necesitamos pares de números aleatorios
        if len(random_nums) % 2 != 0:
            random_nums = random_nums[:-1]
        
        for i in range(0, len(random_nums), 2):
            if i+1 < len(random_nums):
                u1 = random_nums[i]
                u2 = random_nums[i+1]
                
                # Evitar logaritmo de cero
                if u1 <= 0:
                    u1 = 0.0001
                
                # Generar normal estándar con Box-Muller
                z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
                
                # Generar chi-cuadrado para los grados de libertad
                v = np.random.chisquare(df)
                
                # Calcular t-Student
                t = z / np.sqrt(v/df)
                result.append(t)
        
        # Completar si es necesario
        while len(result) < len(random_nums):
            result.append(np.random.standard_t(df))
        
        return result[:len(random_nums)]
    
    @staticmethod
    def f_distribution(random_nums, dfn=1, dfd=1):
        """Distribución F"""
        result = []
        
        # Necesitamos pares de números aleatorios
        if len(random_nums) % 2 != 0:
            random_nums = random_nums[:-1]
        
        for i in range(0, len(random_nums), 2):
            if i+1 < len(random_nums):
                # Generar dos chi-cuadrado independientes
                chi1 = np.random.chisquare(dfn)
                chi2 = np.random.chisquare(dfd)
                
                # Calcular estadístico F
                f = (chi1/dfn) / (chi2/dfd)
                result.append(f)
        
        # Completar si es necesario
        while len(result) < len(random_nums):
            result.append(np.random.f(dfn, dfd))
        
        return result[:len(random_nums)]
    
    @staticmethod
    def geometric(random_nums, p=0.5):
        """Distribución Geométrica"""
        # Número de ensayos Bernoulli hasta el primer éxito
        return [int(np.ceil(np.log(1-r) / np.log(1-p))) for r in random_nums]
    
    @staticmethod
    def negative_binomial(random_nums, n=10, p=0.5):
        """Distribución Binomial Negativa"""
        # Número de ensayos Bernoulli hasta obtener r éxitos
        result = []
        
        for r in random_nums:
            # Aproximación
            x = np.random.negative_binomial(n, p)
            result.append(x)
        
        return result
class numram(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Números Aleatorios y Distribuciones")
        self.resize(900, 700)
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
        """)

        self.setup_ui()
        self.generator = RandomGenerator()
        self.transformer = DistributionTransformer()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Panel de configuración compacto
        config_frame = QFrame()
        config_layout = QHBoxLayout(config_frame)
        config_layout.setContentsMargins(5, 5, 5, 5)
        config_layout.setSpacing(10)
        
        # Primera columna: Método y distribución
        col1_layout = QFormLayout()
        col1_layout.setSpacing(5)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        
        # Selector de método de generación
        self.method_selector = QComboBox()
        self.method_selector.addItems([
            "Mersenne Twister",
            "Xorshift",
            "PCG (Permuted Congruential Generator)",
            "WELL (Well Equidistributed Long-period Linear)",
            "Congruencial Lineal Mixto (MCL)",
            "Congruencial Multiplicativo",
            "Tausworthe / LFSR",
            "Productos Medios",
            "Cuadrático Medio"
        ])
        
        # Selector de distribución
        self.distribution_selector = QComboBox()
        self.distribution_selector.addItems([
            "Uniforme",
            "Normal",
            "Exponencial",
            "Poisson",
            "Binomial",
            "Gamma",
            "Beta",
            "Chi-cuadrado",
            "t-Student",
            "F",
            "Geométrica",
            "Binomial Negativa"
        ])
        self.distribution_selector.currentIndexChanged.connect(self.update_param_widgets)
        
        col1_layout.addRow("Método:", self.method_selector)
        col1_layout.addRow("Distribución:", self.distribution_selector)
        
        # Segunda columna: Cantidad y semilla
        col2_layout = QFormLayout()
        col2_layout.setSpacing(5)
        col2_layout.setContentsMargins(0, 0, 0, 0)
        
        # Número de valores a generar
        self.count_input = QSpinBox()
        self.count_input.setRange(1, 10000)
        self.count_input.setValue(100)
        
        # Semilla opcional
        self.seed_input = QSpinBox()
        self.seed_input.setRange(1, 2**31-1)
        self.seed_input.setValue(12345)
        
        col2_layout.addRow("Cantidad:", self.count_input)
        col2_layout.addRow("Semilla:", self.seed_input)
        
        # Tercera columna: Parámetros de distribución
        # Contenedor para parámetros de distribución
        self.param_container = QStackedWidget()
        
        # 1. Parámetros para Uniforme
        uniform_widget = QWidget()
        uniform_layout = QFormLayout(uniform_widget)
        uniform_layout.setContentsMargins(0, 0, 0, 0)
        uniform_layout.setSpacing(5)
        self.uniform_min = QDoubleSpinBox()
        self.uniform_min.setRange(-1000, 1000)
        self.uniform_min.setValue(0)
        self.uniform_min.setDecimals(2)
        self.uniform_max = QDoubleSpinBox()
        self.uniform_max.setRange(-1000, 1000)
        self.uniform_max.setValue(1)
        self.uniform_max.setDecimals(2)
        uniform_layout.addRow("Mín (a):", self.uniform_min)
        uniform_layout.addRow("Máx (b):", self.uniform_max)
        self.param_container.addWidget(uniform_widget)
        
        # 2. Parámetros para Normal
        normal_widget = QWidget()
        normal_layout = QFormLayout(normal_widget)
        normal_layout.setContentsMargins(0, 0, 0, 0)
        normal_layout.setSpacing(5)
        self.normal_mean = QDoubleSpinBox()
        self.normal_mean.setRange(-1000, 1000)
        self.normal_mean.setValue(0)
        self.normal_mean.setDecimals(2)
        self.normal_std = QDoubleSpinBox()
        self.normal_std.setRange(0.01, 1000)
        self.normal_std.setValue(1)
        self.normal_std.setDecimals(2)
        normal_layout.addRow("Media (μ):", self.normal_mean)
        normal_layout.addRow("Desv. (σ):", self.normal_std)
        self.param_container.addWidget(normal_widget)
        
        # 3. Parámetros para Exponencial
        exp_widget = QWidget()
        exp_layout = QFormLayout(exp_widget)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        exp_layout.setSpacing(5)
        self.exp_lambda = QDoubleSpinBox()
        self.exp_lambda.setRange(0.01, 100)
        self.exp_lambda.setValue(1)
        self.exp_lambda.setDecimals(2)
        exp_layout.addRow("Lambda (λ):", self.exp_lambda)
        self.param_container.addWidget(exp_widget)
        
        # 4. Parámetros para Poisson
        poisson_widget = QWidget()
        poisson_layout = QFormLayout(poisson_widget)
        poisson_layout.setContentsMargins(0, 0, 0, 0)
        poisson_layout.setSpacing(5)
        self.poisson_lambda = QDoubleSpinBox()
        self.poisson_lambda.setRange(0.01, 100)
        self.poisson_lambda.setValue(5)
        self.poisson_lambda.setDecimals(2)
        poisson_layout.addRow("Lambda (λ):", self.poisson_lambda)
        self.param_container.addWidget(poisson_widget)
        
        # 5. Parámetros para Binomial
        binomial_widget = QWidget()
        binomial_layout = QFormLayout(binomial_widget)
        binomial_layout.setContentsMargins(0, 0, 0, 0)
        binomial_layout.setSpacing(5)
        self.binomial_n = QSpinBox()
        self.binomial_n.setRange(1, 1000)
        self.binomial_n.setValue(10)
        self.binomial_p = QDoubleSpinBox()
        self.binomial_p.setRange(0.01, 0.99)
        self.binomial_p.setValue(0.5)
        self.binomial_p.setDecimals(2)
        binomial_layout.addRow("Ensayos (n):", self.binomial_n)
        binomial_layout.addRow("Prob. (p):", self.binomial_p)
        self.param_container.addWidget(binomial_widget)
        
        # 6. Parámetros para Gamma
        gamma_widget = QWidget()
        gamma_layout = QFormLayout(gamma_widget)
        gamma_layout.setContentsMargins(0, 0, 0, 0)
        gamma_layout.setSpacing(5)
        self.gamma_shape = QDoubleSpinBox()
        self.gamma_shape.setRange(0.01, 100)
        self.gamma_shape.setValue(1)
        self.gamma_shape.setDecimals(2)
        self.gamma_scale = QDoubleSpinBox()
        self.gamma_scale.setRange(0.01, 100)
        self.gamma_scale.setValue(1)
        self.gamma_scale.setDecimals(2)
        gamma_layout.addRow("Forma (k):", self.gamma_shape)
        gamma_layout.addRow("Escala (θ):", self.gamma_scale)
        self.param_container.addWidget(gamma_widget)
        
        # 7. Parámetros para Beta
        beta_widget = QWidget()
        beta_layout = QFormLayout(beta_widget)
        beta_layout.setContentsMargins(0, 0, 0, 0)
        beta_layout.setSpacing(5)
        self.beta_alpha = QDoubleSpinBox()
        self.beta_alpha.setRange(0.01, 100)
        self.beta_alpha.setValue(2)
        self.beta_alpha.setDecimals(2)
        self.beta_beta = QDoubleSpinBox()
        self.beta_beta.setRange(0.01, 100)
        self.beta_beta.setValue(2)
        self.beta_beta.setDecimals(2)
        beta_layout.addRow("Alpha (α):", self.beta_alpha)
        beta_layout.addRow("Beta (β):", self.beta_beta)
        self.param_container.addWidget(beta_widget)
        
        # 8. Parámetros para Chi-cuadrado
        chi2_widget = QWidget()
        chi2_layout = QFormLayout(chi2_widget)
        chi2_layout.setContentsMargins(0, 0, 0, 0)
        chi2_layout.setSpacing(5)
        self.chi2_df = QSpinBox()
        self.chi2_df.setRange(1, 100)
        self.chi2_df.setValue(1)
        chi2_layout.addRow("Grados libertad:", self.chi2_df)
        self.param_container.addWidget(chi2_widget)
        
        # 9. Parámetros para t-Student
        t_widget = QWidget()
        t_layout = QFormLayout(t_widget)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_layout.setSpacing(5)
        self.t_df = QSpinBox()
        self.t_df.setRange(1, 100)
        self.t_df.setValue(10)
        t_layout.addRow("Grados libertad:", self.t_df)
        self.param_container.addWidget(t_widget)
        
        # 10. Parámetros para F
        f_widget = QWidget()
        f_layout = QFormLayout(f_widget)
        f_layout.setContentsMargins(0, 0, 0, 0)
        f_layout.setSpacing(5)
        self.f_dfn = QSpinBox()
        self.f_dfn.setRange(1, 100)
        self.f_dfn.setValue(5)
        self.f_dfd = QSpinBox()
        self.f_dfd.setRange(1, 100)
        self.f_dfd.setValue(10)
        f_layout.addRow("GL numerador:", self.f_dfn)
        f_layout.addRow("GL denominador:", self.f_dfd)
        self.param_container.addWidget(f_widget)
        
        # 11. Parámetros para Geométrica
        geo_widget = QWidget()
        geo_layout = QFormLayout(geo_widget)
        geo_layout.setContentsMargins(0, 0, 0, 0)
        geo_layout.setSpacing(5)
        self.geo_p = QDoubleSpinBox()
        self.geo_p.setRange(0.01, 0.99)
        self.geo_p.setValue(0.5)
        self.geo_p.setDecimals(2)
        geo_layout.addRow("Prob. éxito (p):", self.geo_p)
        self.param_container.addWidget(geo_widget)
        
        # 12. Parámetros para Binomial Negativa
        nbinom_widget = QWidget()
        nbinom_layout = QFormLayout(nbinom_widget)
        nbinom_layout.setContentsMargins(0, 0, 0, 0)
        nbinom_layout.setSpacing(5)
        self.nbinom_n = QSpinBox()
        self.nbinom_n.setRange(1, 100)
        self.nbinom_n.setValue(5)
        self.nbinom_p = QDoubleSpinBox()
        self.nbinom_p.setRange(0.01, 0.99)
        self.nbinom_p.setValue(0.5)
        self.nbinom_p.setDecimals(2)
        nbinom_layout.addRow("Éxitos (r):", self.nbinom_n)
        nbinom_layout.addRow("Prob. éxito (p):", self.nbinom_p)
        self.param_container.addWidget(nbinom_widget)
        
        # Botón generar compacto
        self.gen_btn = QPushButton("Generar")
        self.gen_btn.setIcon(QIcon("img/random.png"))
        self.gen_btn.setMinimumHeight(30)
        self.gen_btn.setIconSize(QSize(20, 20))
        self.gen_btn.clicked.connect(self.generar)
        
        # Añadir todo al layout de configuración
        config_layout.addLayout(col1_layout)
        config_layout.addLayout(col2_layout)
        config_layout.addWidget(self.param_container)
        config_layout.addWidget(self.gen_btn)
        
        main_layout.addWidget(config_frame)

        # Layout para la tabla y gráficas
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Tabla de resultados
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        table_header = QLabel("Números Generados")
        table_header.setStyleSheet("font-size: 12px; font-weight: bold; color: #19A7CE; padding: 2px;")
        table_layout.addWidget(table_header)
        
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
        table_layout.addWidget(self.table)
        
        # Gráficas
        graph_frame = QFrame()
        graph_layout = QVBoxLayout(graph_frame)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        graph_layout.setSpacing(0)
        
        graph_header = QLabel("Análisis Gráfico")
        graph_header.setStyleSheet("font-size: 12px; font-weight: bold; color: #19A7CE; padding: 2px;")
        graph_layout.addWidget(graph_header)
        
        self.figure, self.axes = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        self.figure.patch.set_facecolor('#F6F1F1')
        self.axes[0].set_facecolor('#FFFFFF')
        self.axes[1].set_facecolor('#FFFFFF')
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        
        # Añadir tabla y gráficas al layout principal
        content_layout.addWidget(table_frame, 1)
        content_layout.addWidget(graph_frame, 2)
        main_layout.addLayout(content_layout, 1)

        self.setLayout(main_layout)
        
        # Inicializar con la primera distribución
        self.update_param_widgets(0)
        
    def update_param_widgets(self, index):
        """Actualiza los widgets de parámetros según la distribución seleccionada"""
        self.param_container.setCurrentIndex(index)
    
    def generar(self):
        try:
            method = self.method_selector.currentText()
            distribution = self.distribution_selector.currentText()
            count = self.count_input.value()
            seed = self.seed_input.value()
            
            # Para depuración - imprime los valores que se están usando
            print(f"Método: {method}, Distribución: {distribution}, Cantidad: {count}, Semilla: {seed}")
            
            # 1. Generar números aleatorios uniformes con el método seleccionado
            uniform_nums = []
            if method == "Mersenne Twister":
                uniform_nums = self.generator.mersenne_twister(count, seed)
            elif method == "Xorshift":
                uniform_nums = self.generator.xorshift(count, seed)
            elif method == "PCG (Permuted Congruential Generator)":
                uniform_nums = self.generator.pcg(count, seed)
            elif method == "WELL (Well Equidistributed Long-period Linear)":
                uniform_nums = self.generator.well(count, seed)
            elif method == "Congruencial Lineal Mixto (MCL)":
                uniform_nums = self.generator.lcg(count, seed)
            elif method == "Congruencial Multiplicativo":
                uniform_nums = self.generator.mcg(count, seed)
            elif method == "Tausworthe / LFSR":
                uniform_nums = self.generator.tausworthe(count, seed)
            elif method == "Productos Medios":
                uniform_nums = self.generator.middle_square(count, seed)
            elif method == "Cuadrático Medio":
                uniform_nums = self.generator.middle_square_weyl(count, seed)
            
            # 2. Transformar a la distribución deseada
            random_nums = []
            if distribution == "Uniforme":
                a = self.uniform_min.value()
                b = self.uniform_max.value()
                random_nums = self.transformer.uniform(uniform_nums, a, b)
            elif distribution == "Normal":
                mean = self.normal_mean.value()
                std = self.normal_std.value()
                random_nums = self.transformer.normal(uniform_nums, mean, std)
            elif distribution == "Exponencial":
                lambd = self.exp_lambda.value()
                random_nums = self.transformer.exponential(uniform_nums, lambd)
            elif distribution == "Poisson":
                lambd = self.poisson_lambda.value()
                random_nums = self.transformer.poisson(uniform_nums, lambd)
            elif distribution == "Binomial":
                n = self.binomial_n.value()
                p = self.binomial_p.value()
                random_nums = self.transformer.binomial(uniform_nums, n, p)
            elif distribution == "Gamma":
                shape = self.gamma_shape.value()
                scale = self.gamma_scale.value()
                random_nums = self.transformer.gamma(uniform_nums, shape, scale)
            elif distribution == "Beta":
                alpha = self.beta_alpha.value()
                beta = self.beta_beta.value()
                random_nums = self.transformer.beta(uniform_nums, alpha, beta)
            elif distribution == "Chi-cuadrado":
                df = self.chi2_df.value()
                random_nums = self.transformer.chi_squared(uniform_nums, df)
            elif distribution == "t-Student":
                df = self.t_df.value()
                random_nums = self.transformer.t_distribution(uniform_nums, df)
            elif distribution == "F":
                dfn = self.f_dfn.value()
                dfd = self.f_dfd.value()
                random_nums = self.transformer.f_distribution(uniform_nums, dfn, dfd)
            elif distribution == "Geométrica":
                p = self.geo_p.value()
                random_nums = self.transformer.geometric(uniform_nums, p)
            elif distribution == "Binomial Negativa":
                n = self.nbinom_n.value()
                p = self.nbinom_p.value()
                random_nums = self.transformer.negative_binomial(uniform_nums, n, p)
            
            # Preparar la tabla
            self.table.clearContents()
            self.table.setRowCount(min(count, 1000))  # Mostrar máximo 1000 filas
            self.table.setColumnCount(1)  # Solo una columna para los valores
            self.table.setHorizontalHeaderLabels(["Valor"])
            
            # Llenar la tabla
            for i in range(min(count, 1000)):
                # Columna valor
                val_item = QTableWidgetItem(f"{random_nums[i]:.8f}" if isinstance(random_nums[i], float) else f"{random_nums[i]}")
                val_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 0, val_item)
            
            self.table.resizeColumnsToContents()
            
            # Actualizar gráficos
            self.plot_analysis(random_nums, method, distribution)
            
            QMessageBox.information(self, "Generación Completada", 
                                   f"Se han generado {count} números aleatorios usando el método {method} y la distribución {distribution}.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante la generación:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def plot_analysis(self, numbers, method, distribution):
        # Limpiar gráficos anteriores
        for ax in self.axes:
            ax.clear()

        # Ajustar el número de bins para el histograma
        try:
            data_range = max(numbers) - min(numbers)
            if data_range > 0:
                n_bins = int(np.ceil(np.log2(len(numbers)) + 1))
                n_bins = min(max(n_bins, 10), 50)
            else:
                n_bins = 20
        except:
            n_bins = 20

        # Histograma con estilo similar al gráfico de la imagen
        self.axes[0].hist(numbers, bins=n_bins, color='#1976D2', alpha=0.8, edgecolor='white', linewidth=1)

        # Calcular media y desviación para la curva normal (usando datos reales)
        mean = np.mean(numbers)
        std = np.std(numbers)

        # Crear valores x para la curva normal
        x = np.linspace(min(numbers), max(numbers), 200)
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std)**2)

        # Escalar la curva para que encaje con el histograma
        scale_factor = len(numbers) * (max(numbers) - min(numbers)) / n_bins
        y_scaled = y * scale_factor

        # Graficar la curva normal en rojo
        self.axes[0].plot(x, y_scaled, color='red', linewidth=2, label=f"Normal(μ={mean:.2f}, σ={std:.2f})")

        self.axes[0].set_title("Distribución", fontweight='bold', color="#0b2447")
        self.axes[0].set_xlabel("Valor", fontweight='bold')
        self.axes[0].set_ylabel("Frecuencia", fontweight='bold')
        self.axes[0].grid(True, linestyle='--', alpha=0.7)
        self.axes[0].legend()

        # Gráfico de dispersión secuencial (igual que antes)
        self.axes[1].plot(range(len(numbers)), numbers, 'o', markersize=3, color='#1976D2', alpha=0.6)
        self.axes[1].set_title("Secuencia", fontweight='bold', color="#0b2447")
        self.axes[1].set_xlabel("Índice", fontweight='bold')
        self.axes[1].set_ylabel("Valor", fontweight='bold')
        self.axes[1].grid(True, linestyle='--', alpha=0.7)

        self.axes[0].set_ylim(bottom=0)

        min_val = min(numbers)
        max_val = max(numbers)
        padding = (max_val - min_val) * 0.05
        self.axes[1].set_ylim(min_val - padding, max_val + padding)

        for ax in self.axes:
            for spine in ax.spines.values():
                spine.set_color('#1976D2')
                spine.set_linewidth(1.5)

        method_short = method.split(" ")[0]
        self.figure.suptitle(f"{method_short} - {distribution}",
                            fontsize=12, fontweight='bold', color="#0b2447")

        self.figure.tight_layout()
        self.canvas.draw()
