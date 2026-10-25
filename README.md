# Visión en capas

Prototipo académico en Python para detección de colores, identificación de formas geométricas y conteo de objetos con OpenCV y Streamlit.

## Requisitos

- Python 3.10 o superior.
- Visual Studio Code.

## Instalación en Windows

Abre la carpeta del proyecto en Visual Studio Code y ejecuta en la terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/create_examples.py
```

Si PowerShell bloquea la activación, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` o usa directamente `.venv\Scripts\python.exe`.

## Ejecución

```powershell
streamlit run app.py
```

Se abrirá una dirección local, normalmente `http://localhost:8501`. También puedes cargar tus propias imágenes desde el panel lateral.

## Pruebas

```powershell
pytest -q
```

Las pruebas verifican la clasificación de un triángulo, la detección de un círculo rojo y el resumen de conteos. No sustituyen la evaluación con las fotografías reales de la aplicación del equipo.

## Estructura

```text
app.py                       Interfaz gráfica Streamlit
src/image_processor.py       Preprocesamiento y detección
scripts/create_examples.py   Generador de imagen de prueba
tests/test_image_processor.py Pruebas automatizadas
assets/example_shapes.png    Imagen de ejemplo generada
requirements.txt             Dependencias
```

## Flujo académico implementado

La interfaz presenta explícitamente: imagen original, preprocesamiento, extracción de información, resultado e interpretación. El detector usa HSV para segmentar colores, operaciones morfológicas para limpiar las máscaras y contornos para estimar forma, centro, área y confianza aproximada.

