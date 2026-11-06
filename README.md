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
* **Stack en Python:** Desarrollado con **FastAPI** y templates **Jinja2**, ofreciendo velocidad ultrarrápida, SEO con OpenGraph para previsualizaciones atractivas en redes sociales y APIs REST listas para consumir.
* **Fácil de mantener:** Los productos, precios y fotos se administran desde un archivo simple (`app/data/products.json`).
* **Listo para desplegar:** Incluye configuración para Render, Railway, Fly.io o cualquier servidor con Docker.

---

## 🚀 Cómo ejecutar en desarrollo

1. **Crear y activar entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar el servidor:**
   ```bash
   python run.py
   # o bien:
   uvicorn app.main:app --reload --port 8000
   ```

4. Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

---

## 🛠️ Estructura del proyecto

```text
facu_site/
├── app/
│   ├── data/
│   │   └── products.json    # Catálogo de tortas, precios, porciones y fotos
│   ├── static/
│   │   ├── css/style.css    # Estilos y animaciones táctiles móviles
│   │   └── js/app.js        # Lógica del carrito y armado de pedido a WhatsApp
│   ├── templates/
│   │   └── index.html       # Interfaz completa y responsiva
│   └── main.py              # Aplicación FastAPI, rutas y APIs
├── Dockerfile               # Contenedor listo para producción
├── Procfile                 # Despliegue en Render / Railway / Heroku
├── requirements.txt         # Dependencias Python mínimas y livianas
├── run.py                   # Script de arranque rápido
└── README.md
```

---

## ☁️ Opciones de despliegue sugeridas

1. **Render / Railway (PaaS sin costo inicial o bajo costo):**
   * Conectar el repositorio de GitHub.
   * Render detecta automáticamente el `requirements.txt` o `Procfile`.
   * Comando de inicio: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Fly.io / VPS con Docker:**
   * Simplemente ejecutar `fly launch` o `docker build -t facu-site . && docker run -p 8000:8000 facu-site`.

3. **PythonAnywhere:**
   * Compatible con aplicaciones WSGI/ASGI estándar de Python.

---

## 👤 Información del negocio
* **Pastelero:** Facundo Juárez Downes
* **WhatsApp:** `+54 9 11 6454-6785`
* **Instagram:** `@juarezdownes`
* **Localidad:** Hurlingham, Buenos Aires
