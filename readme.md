# 🧮 NeuroMate - Sistema Matemático

Bienvenido a **NeuroMate**, una herramienta matemática avanzada desarrollada en Python con PyQt5.  
Este sistema modular te permite realizar operaciones matemáticas complejas de manera organizada, intuitiva y con una interfaz gráfica amigable.

---

## 🚀 ¿Cómo comenzar?

El archivo principal para ejecutar la aplicación es:

```bash
python neuromate.py
```

> 📝 Asegúrate de tener Python 3.7+ instalado y las librerías necesarias (PyQt5, entre otras).

### 🔧 Alternativas para ejecutar:

- **Visual Studio Code**:
  1. Abre la carpeta del proyecto en VS Code.
  2. Haz clic derecho sobre `neuromate.py`.
  3. Selecciona `Run Python File in Terminal`.

- **Desde consola/terminal**:  
  Navega al directorio del proyecto y ejecuta:

```bash
python neuromate.py
```

---

## 📦 Cómo generar un ejecutable (.exe)

Para crear un archivo ejecutable independiente para Windows, usa PyInstaller con el siguiente comando:

```bash
pyinstaller --noconfirm --windowed --onefile --add-data "img;img" --add-data "docs;docs" --icon=img/icon.ico neuromate.py
```

- Este comando empaqueta todos los recursos (imágenes, documentos) y el ícono en un solo `.exe`.  
- Asegúrate de tener instalado PyInstaller (`pip install pyinstaller`).

---

## 🧩 Estructura del proyecto

El sistema está organizado en módulos independientes que facilitan la mantenibilidad y extensión:

| Archivo            | Descripción                                                        |
|--------------------|-------------------------------------------------------------------|
| `neuromate.py`     | 🧭 Archivo principal y punto de entrada de la aplicación.         |
| `calculadora.py`   | ➕ Calculadora y operaciones básicas con matrices.                 |
| `fun2d.py`         | 📈 Gráficas y funciones matemáticas 2D y 3D.                      |
| `oppoli.py`        | 🧮 Operaciones con polinomios.                                    |
| `opvect.py`        | 🧲 Operaciones con vectores y valores propios.                    |
| `acercade.py`      | ℹ️ Información sobre el sistema.                                  |
| `vyvpropios.py`    | 🧮 Cálculo de vectores y valores propios (módulo específico).     |
| `aleatorios.py`    | 🎲 Generación de números aleatorios.                              |
| `montecarlo.py`    | 🔄 Simulaciones Montecarlo.                                       |
| `predictivo.py`    | 📊 Sistema de predicción matemática.                             |
| `img/`             | 🖼 Carpeta con imágenes e íconos utilizados en la interfaz.      |
| `docs/`            | 📄 Documentación adicional (si aplica).                           |

> ⚠️ Cada módulo está aislado para evitar que fallos en uno afecten al resto del sistema.

---

## 💡 Características principales

- ✅ **Modularidad:** Cada funcionalidad está contenida en módulos separados.  
- ✅ **Interfaz gráfica intuitiva:** Navegación sencilla mediante un menú lateral.  
- ✅ **Tolerancia a errores:** El sistema captura excepciones y sigue funcionando.  
- ✅ **Múltiples funcionalidades matemáticas:**  
  - Operaciones con matrices y sistemas lineales.  
  - Cálculo con polinomios y vectores.  
  - Gráficas 2D y 3D.  
  - Resolución de ecuaciones diferenciales ordinarias (EDO).  
  - Cálculo de vectores y valores propios.  
  - Generación de números aleatorios.  
  - Simulaciones de Montecarlo.  
  - Sistema de predicción matemática.

---



_Aquí puedes añadir imágenes de la interfaz para mostrar cómo funciona el sistema._

---

## 🛠 Requisitos

- Python 3.7 o superior.  
- Librerías:  
  - PyQt5  
  - Otras librerías estándar de Python (según módulos específicos).

---

## 📬 Contacto

- **Ronny Arellano Urgiles**  
- Correo: rarellanou@unemi.edu.ec  
- Universidad Estatal de Milagro (UNEMI) - Software, sexto semestre  

---

Gracias por usar NeuroMate. ¡Esperamos que te sea de gran utilidad para tus proyectos matemáticos!
