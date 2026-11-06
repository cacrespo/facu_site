# 🍰 Facu de las Tortas - Sitio Web Oficial (Hurlingham)

Sitio web oficial, catálogo interactivo y generador de pedidos por WhatsApp para **Facundo Juárez Downes** ("*Facu de las tortas*"), reconocido y querido pastelero de Hurlingham, Buenos Aires, con más de 20 años de historia endulzando el barrio.

---

## 📱 Características principales

* **100% Mobile-First:** Diseñado y optimizado especialmente para teléfonos móviles, navegación táctil ágil, botones grandes y estética pastelera cálida y artesanal.
* **Catálogo interactivo con filtros:** Filtro rápido por categorías (*Especialidades, Tartas, Tortas enteras, Porciones*).
* **Carrito y Generador de pedidos por WhatsApp:**
  * Al agregar productos se activa una barra flotante inferior.
  * Modal deslizante estilo *bottom-sheet* para ajustar cantidades, indicar nombre, dirección o fecha deseada.
  * Botón directo que abre WhatsApp (`+54 9 11 6454-6785`) con el mensaje prolijo y total calculado listo para enviar.
* **Stack en Python con `uv`:** Gestión ultra-rápida de entornos y bibliotecas con **`uv`**, servidor moderno con **FastAPI** y templates **Jinja2**.
* **Fácil de mantener:** Los productos, precios y fotos se administran desde un archivo simple (`app/data/products.json`).
* **Listo para desplegar:** Incluye configuración para Render, Railway, Fly.io o Docker con la imagen oficial de `uv`.

---

## ⚡ Gestión con `uv` y desarrollo local

El proyecto utiliza **`uv`** de Astral para la gestión del entorno y las dependencias.

### 1. Sincronizar el entorno virtual
```bash
uv sync
```
*(Crea automáticamente `.venv` y sincroniza todas las bibliotecas con `uv.lock` en milisegundos)*.

### 2. Ejecutar el servidor local
```bash
uv run python run.py
```
*(O bien: `uv run uvicorn app.main:app --reload --port 8000`)*

Luego abrís en tu navegador: **[http://localhost:8000](http://localhost:8000)**

### 3. Agregar nuevas bibliotecas (si fueran necesarias)
```bash
uv add nombre-de-libreria
```

---

## 🛠️ Estructura del proyecto

```text
facu_site/
├── pyproject.toml           # Configuración del proyecto y dependencias de uv
├── uv.lock                  # Lockfile determinista y ultra-rápido de uv
├── requirements.txt         # Export para plataformas PaaS tradicionales
├── app/
│   ├── data/
│   │   └── products.json    # Catálogo de tortas, precios, porciones y fotos
│   ├── static/
│   │   ├── css/style.css    # Estilos y animaciones táctiles móviles
│   │   └── js/app.js        # Lógica del carrito y armado de pedido a WhatsApp
│   ├── templates/
│   │   └── index.html       # Interfaz completa y responsiva
│   └── main.py              # Aplicación FastAPI, rutas y APIs
├── Dockerfile               # Contenedor optimizado con ghcr.io/astral-sh/uv
├── Procfile                 # Despliegue en Render / Railway / Heroku
├── run.py                   # Script de arranque rápido
└── README.md
```

---

## ☁️ Opciones de despliegue

1. **Render / Railway / Heroku:**
   * Reconoce el `Procfile` y `requirements.txt` automáticamente.
   * Comando de inicio: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Fly.io / VPS con Docker:**
   * El `Dockerfile` utiliza la imagen oficial optimizada `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
   * Ejecutar:
     ```bash
     docker build -t facu-site .
     docker run -p 8000:8000 facu-site
     ```

---

## 👤 Información del negocio
* **Pastelero:** Facundo Juárez Downes
* **WhatsApp:** `+54 9 11 6454-6785`
* **Instagram:** `@juarezdownes`
* **Localidad:** Hurlingham, Buenos Aires
