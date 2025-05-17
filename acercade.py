from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                         QGridLayout, QHBoxLayout, QFrame, QFileDialog, QSizePolicy)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
import os
import shutil
import sys

class AcercaDe(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroMate - Acerca de")
        self.setGeometry(250, 250, 800, 600)
        
        # Obtener la ruta base de la aplicación para cargar recursos correctamente
        if getattr(sys, 'frozen', False):
            # Si estamos ejecutando como un ejecutable (.exe)
            self.base_path = sys._MEIPASS
        else:
            # Si estamos ejecutando en modo desarrollo
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Usar ruta absoluta para el ícono
        icon_path = os.path.join(self.base_path, "img", "icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Establecer el color de fondo base para todo el widget
        self.setStyleSheet("""
            QWidget {
                background-color: #fdfaf6;
                color: #2e2e2e;
                font-family: 'Segoe UI';
            }
            QLabel#titulo {
                font-weight: bold;
                font-size: 28px;
                color: #1a3c73;
                margin-bottom: 20px;
            }
            QLabel#subtitulo {
                font-weight: bold; 
                font-size: 20px;
                color: #1a3c73;
                margin-top: 10px;
                margin-bottom: 15px;
            }
            QLabel#info_label {
                font-weight: bold;
                font-size: 16px;
                color: #1a3c73;
            }
            QLabel#info_value {
                font-size: 16px;
                color: #333;
            }
            QFrame {
                border: none;
            }
            QPushButton#cerrar_btn {
                background-color: #3dbff3;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton#cerrar_btn:hover {
                background-color: #63cdf9;
            }
            QPushButton#doc_button {
                color: #333;
                border: 1px solid #ccc;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 160px;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton#doc_button:hover {
                background-color: #f0f0f0;
            }
        """)

        # Layout principal horizontal para las dos columnas
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Columna izquierda para información
        left_column = QVBoxLayout()
        left_column.setContentsMargins(20, 20, 10, 20)
        
        # Columna derecha para documentación
        right_column = QVBoxLayout()
        right_column.setContentsMargins(10, 20, 20, 20)

        # Header con logo y título
        header_layout = QHBoxLayout()
        
        # Logo con ruta absoluta
        logo_label = QLabel()
        pixmap = QPixmap(icon_path)
        logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(64, 64)
        
        # Título
        titulo = QLabel("Acerca de NeuroMate")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        
        left_column.addLayout(header_layout)
        
        # Frame tipo tabla para la información
        frame_tabla = QFrame()
        frame_tabla.setObjectName("tabla")
        tabla_layout = QGridLayout()
        tabla_layout.setHorizontalSpacing(30)
        tabla_layout.setVerticalSpacing(15)
        tabla_layout.setContentsMargins(30, 30, 30, 30)
        frame_tabla.setLayout(tabla_layout)

        datos = [
            ("Autor:", "Ronny Arellano Urgiles"),
            ("Carrera:", "Ingeniería de Software"),
            ("Semestre:", "Sexto"),
            ("Año Académico:", "2025"),
            ("Profesor:", "Morales Torres Fabricio"),
            ("Materia:", "Modelos Matemáticos"),
        ]

        for i, (etiqueta, valor) in enumerate(datos):
            label_etiqueta = QLabel(etiqueta)
            label_etiqueta.setObjectName("info_label")
            label_etiqueta.setStyleSheet("background: transparent;")
            label_valor = QLabel(valor)
            label_valor.setObjectName("info_value")
            label_valor.setStyleSheet("background: transparent;")

            tabla_layout.addWidget(label_etiqueta, i, 0, alignment=Qt.AlignRight)
            tabla_layout.addWidget(label_valor, i, 1, alignment=Qt.AlignLeft)

        left_column.addWidget(frame_tabla, 1)
        
        # Botón para cerrar en la columna izquierda
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setObjectName("cerrar_btn")
        self.btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cerrar)
        
        left_column.addLayout(btn_layout)
        left_column.addStretch()

        # Sección de documentación en la columna derecha
        docs_titulo = QLabel("Documentación")
        docs_titulo.setObjectName("subtitulo")
        docs_titulo.setAlignment(Qt.AlignCenter)
        right_column.addWidget(docs_titulo)
        
        frame_docs = QFrame()
        frame_docs.setObjectName("documentacion")
        docs_layout = QVBoxLayout()
        docs_layout.setContentsMargins(20, 20, 20, 20)
        frame_docs.setLayout(docs_layout)

        # Crear botones de documentación con mejor diseño
        documentos = [
            ("Manual de Usuario", "manualdeusuario.pdf"),
            ("Ficha Técnica", "ficha_tecnica.pdf"),
            ("Informe Formal", "informe_formal.pdf")
        ]
        
        # Ruta absoluta para el icono PDF
        pdf_icon_path = os.path.join(self.base_path, "img", "pdf_icon.png")
        
        for titulo, archivo in documentos:
            btn = QPushButton(titulo)
            btn.setObjectName("doc_button")
            btn.setIcon(QIcon(pdf_icon_path))
            btn.setIconSize(QSize(32, 32))
            btn.clicked.connect(lambda checked, f=archivo: self.abrir_documento(f))
            docs_layout.addWidget(btn)
            docs_layout.addSpacing(10)  # Espacio entre botones
        
        docs_layout.addStretch()
        right_column.addWidget(frame_docs, 1)
        right_column.addStretch()

        # Añadir columnas al layout principal
        main_layout.addLayout(left_column, 3)  # Proporción 3
        main_layout.addLayout(right_column, 2)  # Proporción 2
        
    def abrir_documento(self, nombre_archivo):
        """
        Abre un cuadro de diálogo para guardar el documento seleccionado
        """
        # Usar ruta absoluta para los documentos
        ruta_docs = os.path.join(self.base_path, "docs")
        ruta_completa = os.path.join(ruta_docs, nombre_archivo)
        
        if os.path.exists(ruta_completa):
            # Abrir diálogo para guardar como
            ruta_destino, _ = QFileDialog.getSaveFileName(
                self, 
                f"Guardar {nombre_archivo}", 
                nombre_archivo,
                "Archivos PDF (*.pdf)"
            )
            
            if ruta_destino:
                try:
                    # Copiar el archivo al destino seleccionado
                    shutil.copy2(ruta_completa, ruta_destino)
                except Exception as e:
                    print(f"Error al guardar el documento: {e}")
        else:
            # Si el archivo no existe, mostrar un mensaje 
            print(f"Error: No se encuentra el archivo {nombre_archivo} en la carpeta docs")