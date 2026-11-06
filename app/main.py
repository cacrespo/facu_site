import json
import urllib.parse
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Facu de las Tortas - Hurlingham",
    description="Sitio oficial y catálogo de Facundo Juárez Downes en Hurlingham",
    version="1.0.0",
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Configurar templates de Jinja2
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Configuración del negocio
BUSINESS_INFO = {
    "name": "Facu de las Tortas",
    "full_name": "Facundo Juárez Downes",
    "tagline": "Más de 20 años endulzando los hogares y comercios de Hurlingham",
    "phone_display": "11 6454-6785",
    "phone_raw": "5491164546785",
    "instagram": "juarezdownes",
    "instagram_url": "https://www.instagram.com/juarezdownes/",
    "tiktok_url": "https://www.tiktok.com/@juarezdownes",
    "email": "fmjuarez82@gmail.com",
    "location": "Hurlingham, Buenos Aires",
    "coverage_areas": ["Hurlingham centro", "Villa Tesei", "William Morris", "Alrededores"],
    "payment_methods": ["Mercado Pago", "Transferencia bancaria", "Efectivo al recibir"],
    "experience_years": "Más de 20 años",
}


def load_products():
    data_path = BASE_DIR / "data" / "products.json"
    if not data_path.exists():
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def home(request: Request):
    products = load_products()
    categories = [
        {"id": "todos", "label": "Todo el menú"},
        {"id": "destacados", "label": "⭐ Especialidades"},
        {"id": "tartas", "label": "🥧 Tartas"},
        {"id": "tortas", "label": "🎂 Tortas Enteras"},
        {"id": "porciones", "label": "🍰 Porciones & Dulces"},
    ]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "business": BUSINESS_INFO,
            "products": products,
            "categories": categories,
        },
    )


@app.get("/api/products")
def get_products(category: Optional[str] = None):
    products = load_products()
    if category and category != "todos":
        products = [p for p in products if p.get("category") == category]
    return products


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    products = load_products()
    for product in products:
        if product.get("id") == product_id:
            return product
    raise HTTPException(status_code=404, detail="Producto no encontrado")


class OrderItem(BaseModel):
    id: str
    name: str
    quantity: int
    price: float


class OrderRequest(BaseModel):
    items: List[OrderItem]
    customer_name: Optional[str] = ""
    delivery_type: Optional[str] = "Entrega en Hurlingham"
    address: Optional[str] = ""
    delivery_date: Optional[str] = ""
    notes: Optional[str] = ""


@app.post("/api/orders/whatsapp-link")
def create_whatsapp_link(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="El pedido debe tener al menos un producto.")

    lines = [
        "👋 ¡Hola Facu! Te contacto desde tu página web para hacer un pedido:",
        "",
        "🍰 *DETALLE DEL PEDIDO:*",
    ]
    total = 0
    for it in order.items:
        subtotal = it.price * it.quantity
        total += subtotal
        lines.append(f"• {it.quantity}x {it.name} - ${subtotal:,.0f}".replace(",", "."))

    lines.append("")
    lines.append(f"💰 *Total estimado:* ${total:,.0f}".replace(",", "."))
    lines.append("")

    if order.customer_name:
        lines.append(f"👤 *A nombre de:* {order.customer_name}")
    if order.delivery_type:
        lines.append(f"📍 *Modalidad:* {order.delivery_type}")
    if order.address:
        lines.append(f"🏠 *Dirección/Zona:* {order.address}")
    if order.delivery_date:
        lines.append(f"📅 *Para la fecha:* {order.delivery_date}")
    if order.notes:
        lines.append(f"📝 *Aclaraciones:* {order.notes}")

    lines.append("")
    lines.append("¿Cómo coordinamos el pago y horario? ¡Muchas gracias!")

    raw_text = "\n".join(lines)
    encoded_text = urllib.parse.quote(raw_text)
    wa_url = f"https://wa.me/{BUSINESS_INFO['phone_raw']}?text={encoded_text}"

    return {
        "url": wa_url,
        "message": raw_text,
        "total": total,
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Facu de las Tortas", "version": "1.0.0"}
