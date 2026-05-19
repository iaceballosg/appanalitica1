# 🏥 Mortalidad en Colombia — 2019

Dashboard interactivo de análisis de defunciones no fetales en Colombia para el año 2019, construido con **Python + Plotly Dash**.

Introducción del proyecto: 
 Se desarrolla una aplicación web dinámica utilizando Plotly y Dash en el lenguaje de programación Python. La aplicación integra informes gráficos interactivos que facilitan la interpretación de los datos y permitan una exploración visual intuitiva. Además, se despliega en Render, asegurando su accesibilidad en línea.

Objetivo: Se analiza la mortalidad en Colombia para el año 2019.

Estructura del proyecto: 
mortalidad_colombia_2019/
├── app.py              ← Aplicación Dash principal
├── prepare_data.py     ← Script para regenerar el parquet desde Excel
├── data_2019.parquet   ← Datos procesados (~15 MB, listos para despliegue)
| se cambia a data_2019.csv por falla en la lectura del parquet
├── requirements.txt    ← Dependencias exactas
├── Procfile            ← Para Render / Railway
├── render.yaml         ← Config automática para Render
├── runtime.txt         ← Python 3.12
├── README.md           ← Guía completa

Requisitos: Librerías y versiones necesarias para ejecutar la aplicación.
 pandas as pd
 plotly.express as px
 plotly.graph_objects as go
 dash import Dash, dcc, html, Input, Output, callback
 os


Despliegue: 

Una vez el repositorio este en GitHub
render.com → New → Web Service → Connect GitHub
Render detecta automáticamente el render.yaml
Haz clic en Deploy — listo.

Software: Herramientas utilizadas (Python, Dash, render, visual studio).


## 📊 Visualizaciones incluidas

| Gráfico | Descripción |
|---|---|
| KPIs dinámicos | Total defunciones, % naturales, homicidios, causa principal |
| Defunciones por mes | Barras mensuales con gradiente |
| Top 10 departamentos | Barras horizontales comparativas |
| Top 15 causas (CIE-10) | Causas con descripción completa al hover |
| Manera de muerte | Gráfico de pie (natural, homicidio, accidente, suicidio…) |
| Por sexo | Donut masculino/femenino |
| Pirámide poblacional | Población fallecida por edad y sexo |
| Sitio de defunción | Hospital, domicilio, vía pública… |
| Área de defunción | Cabecera, centro poblado, rural |
| Manera × sexo | Barras agrupadas |
| Mapa de calor | Departamento × mes |

## 🔧 Requisitos

- Python ≥ 3.11
- Archivos fuente DANE (ver sección de datos)

## 🚀 Ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/mortalidad-colombia-2019.git
cd mortalidad-colombia-2019

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Preparar datos (solo una vez)
# Copiar los 3 archivos DANE en el directorio raíz:
#   - Anexo1_NoFetal2019_CE_15-03-23.xlsx
#   - Anexo2_CodigosDeMuerte_CE_15-03-23.xlsx
#   - Divipola_CE_.xlsx
python prepare_data.py

# 5. Ejecutar la aplicación
python app.py
```

Abrir en el navegador: http://localhost:8050

## 📁 Datos fuente

Archivos del DANE — Estadísticas Vitales Colombia 2019:
- `Anexo1_NoFetal2019_CE_15-03-23.xlsx` — Registro de 244.355 defunciones no fetales
- `Anexo2_CodigosDeMuerte_CE_15-03-23.xlsx` — Catálogo CIE-10
- `Divipola_CE_.xlsx` — División político-administrativa

> **Nota:** Los archivos `.xlsx` originales **no se incluyen** en el repositorio (`.gitignore`) por su tamaño. El archivo `data_2019.parquet` procesado sí debe incluirse.

## ☁️ Despliegue en Render (gratuito)

### Pasos

1. **Generar el parquet localmente** (ver paso 4 de ejecución local).
2. Subir `data_2019.parquet` al repositorio (es pequeño ~15 MB).
3. Crear cuenta en [render.com](https://render.com).
4. **New → Web Service → Connect GitHub repo**.
5. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Plan:** Free
6. Hacer clic en **Deploy**.

El archivo `render.yaml` ya automatiza esta configuración.

## ☁️ Despliegue en Railway

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login y despliegue
railway login
railway init
railway up
```

## ☁️ Despliegue en Google App Engine

```bash
# Instalar Google Cloud CLI, luego:
gcloud app deploy
```

Crear `app.yaml`:
```yaml
runtime: python312
entrypoint: gunicorn app:server --bind :$PORT --workers 2
```

## 🗂️ Estructura del proyecto

```
mortalidad-colombia-2019/
├── app.py              # Aplicación Dash principal
├── prepare_data.py     # Script de preparación de datos
├── data_2019.parquet   # Datos procesados (incluir en repo)
├── requirements.txt    # Dependencias Python
├── Procfile            # Para Render/Railway/Heroku
├── render.yaml         # Configuración automática Render
├── runtime.txt         # Versión de Python
└── README.md
```

## 🔍 Fuentes

- DANE — [dane.gov.co](https://www.dane.gov.co) — Estadísticas Vitales
- Clasificación Internacional de Enfermedades CIE-10 — OPS/OMS

## 📄 Licencia

MIT — uso libre con atribución.
