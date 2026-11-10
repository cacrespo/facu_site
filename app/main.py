import hashlib
import json
import os
import re
import time
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

# Configuración de seguridad para el Administrador
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "facu2024")
SECRET_KEY = os.getenv("SECRET_KEY", "facu-super-secret-key-2024")


def get_admin_token() -> str:
    return hashlib.sha256(f"{ADMIN_PASSWORD}-{SECRET_KEY}".encode()).hexdigest()


def is_admin_authenticated(request: Request) -> bool:
    token = request.cookies.get("admin_session")
    return token == get_admin_token()


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
    "support": {
        "title": "Un mimo para la salud de Facu",
        "alias": "juarezdownes.tortas",  # Alias oficial de Mercado Pago
        "cbu_cvu": "0000003100012345678901",
        "holder": "Facundo Juárez Downes",
        "entity": "Mercado Pago / Cuenta Bancaria",
    },
}

CATEGORY_LABELS = {
    "destacados": "⭐ Especialidades",
    "tartas": "🥧 Tartas Dulces",
    "tortas": "🎂 Tortas Enteras",
    "porciones": "🍰 Porciones & Merienda",
}


def load_settings():
    data_path = BASE_DIR / "data" / "settings.json"
    defaults = {
        "phone_display": "11 6454-6785",
        "phone_raw": "5491164546785",
        "whatsapp_greeting": "👋 ¡Hola Facu! Te contacto desde tu página web para hacer un pedido:",
        "whatsapp_footer": "¿Cómo coordinamos el pago y horario? ¡Muchas gracias!",
        "support_alias": "juarezdownes.tortas",
        "support_holder": "Facundo Juárez Downes",
        "support_entity": "Mercado Pago / Cuenta Digital",
        "support_note": "💙 *Colaboración voluntaria:* Me gustaría sumar un aporte de corazón para tus medicamentos.",
    }
    if not data_path.exists():
        return defaults
    try:
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
            defaults.update(data)
            return defaults
    except Exception:
        return defaults


def save_settings(settings: dict):
    data_path = BASE_DIR / "data" / "settings.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_business_info():
    st = load_settings()
    return {
        "name": "Facu de las Tortas",
        "full_name": "Facundo Juárez Downes",
        "tagline": "Más de 20 años endulzando los hogares y comercios de Hurlingham",
        "phone_display": st.get("phone_display", "11 6454-6785"),
        "phone_raw": st.get("phone_raw", "5491164546785"),
        "instagram": "juarezdownes",
        "instagram_url": "https://www.instagram.com/juarezdownes/",
        "tiktok_url": "https://www.tiktok.com/@juarezdownes",
        "email": "fmjuarez82@gmail.com",
        "location": "Hurlingham, Buenos Aires",
        "coverage_areas": ["Hurlingham centro", "Villa Tesei", "William Morris", "Alrededores"],
        "payment_methods": ["Mercado Pago", "Transferencia bancaria", "Efectivo al recibir"],
        "experience_years": "Más de 20 años",
        "support": {
            "title": "Un mimo para la salud de Facu",
            "alias": st.get("support_alias", "juarezdownes.tortas"),
            "holder": st.get("support_holder", "Facundo Juárez Downes"),
            "entity": st.get("support_entity", "Mercado Pago / Cuenta Digital"),
        },
        "settings": st,
    }


def load_products():
    data_path = BASE_DIR / "data" / "products.json"
    if not data_path.exists():
        return []
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def save_products(products: list):
    data_path = BASE_DIR / "data" / "products.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def load_reviews():
    data_path = BASE_DIR / "data" / "reviews.json"
    if not data_path.exists():
        return []
    try:
        with open(data_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_reviews(reviews: list):
    data_path = BASE_DIR / "data" / "reviews.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


@app.api_route("/", methods=["GET", "HEAD"])
def home(request: Request):
    products = load_products()
    reviews = [r for r in load_reviews() if r.get("is_approved", True)]
    categories = [
        {"id": "todos", "label": "Todo el menú"},
        {"id": "destacados", "label": "⭐ Especialidades"},
        {"id": "tartas", "label": "🥧 Tartas"},
        {"id": "tortas", "label": "🎂 Tortas Enteras"},
        {"id": "porciones", "label": "🍰 Porciones & Dulces"},
    ]
    featured_product = next((p for p in products if p.get("is_featured")), None)
    if not featured_product and products:
        featured_product = products[0]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "business": get_business_info(),
            "products": products,
            "featured_product": featured_product,
            "categories": categories,
            "reviews": reviews,
        },
    )


@app.get("/api/products")
def get_products(category: str | None = None):
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
    items: list[OrderItem]
    customer_name: str | None = ""
    delivery_type: str | None = "Entrega en Hurlingham"
    address: str | None = ""
    delivery_date: str | None = ""
    notes: str | None = ""


@app.post("/api/orders/whatsapp-link")
def create_whatsapp_link(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="El pedido debe tener al menos un producto.")

    st = load_settings()
    lines = [
        st.get(
            "whatsapp_greeting",
            "👋 ¡Hola Facu! Te contacto desde tu página web para hacer un pedido:",
        ),
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
    lines.append(st.get("whatsapp_footer", "¿Cómo coordinamos el pago y horario? ¡Muchas gracias!"))

    raw_text = "\n".join(lines)
    encoded_text = urllib.parse.quote(raw_text)
    phone = st.get("phone_raw", "5491164546785")
    wa_url = f"https://wa.me/{phone}?text={encoded_text}"

    return {
        "url": wa_url,
        "message": raw_text,
        "total": total,
    }


class ReviewCreate(BaseModel):
    name: str
    neighborhood: str | None = "Hurlingham"
    rating: int = 5
    comment: str


@app.get("/api/reviews")
def get_reviews():
    reviews = load_reviews()
    return [r for r in reviews if r.get("is_approved", True)]


@app.post("/api/reviews")
def submit_review(review: ReviewCreate):
    name = review.name.strip()
    comment = review.comment.strip()
    if not name or not comment:
        raise HTTPException(status_code=400, detail="Nombre y comentario son requeridos.")

    rating = max(1, min(5, review.rating))
    neighborhood = review.neighborhood.strip() if review.neighborhood else "Hurlingham"

    reviews = load_reviews()
    new_rev = {
        "id": f"rev-{int(time.time())}",
        "name": name,
        "neighborhood": neighborhood,
        "rating": rating,
        "comment": comment,
        "date": time.strftime("%d/%m/%Y"),
        "is_approved": True,
    }
    reviews.insert(0, new_rev)
    save_reviews(reviews)
    return {"success": True, "review": new_rev}


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Facu de las Tortas", "version": "1.0.0"}


# ==========================================
# RUTAS DE ADMINISTRACIÓN (PANEL DE CONTROL)
# ==========================================


@app.get("/admin/login")
def admin_login_page(request: Request):
    if is_admin_authenticated(request):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": None},
    )


@app.post("/admin/login")
def admin_login_submit(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=get_admin_token(),
            httponly=True,
            max_age=60 * 60 * 24 * 30,  # 30 días
            samesite="lax",
        )
        return response
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": "Contraseña incorrecta. Por favor volvé a intentar."},
        status_code=401,
    )


@app.get("/admin/logout")
def admin_logout():
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@app.get("/admin")
def admin_dashboard(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    products = load_products()
    settings = load_settings()
    reviews = load_reviews()
    saved = request.query_params.get("saved") == "1"
    deleted = request.query_params.get("deleted") == "1"
    settings_saved = request.query_params.get("settings_saved") == "1"
    review_toggled = request.query_params.get("review_toggled") == "1"
    review_deleted = request.query_params.get("review_deleted") == "1"

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "products": products,
            "settings": settings,
            "reviews": reviews,
            "saved": saved,
            "deleted": deleted,
            "settings_saved": settings_saved,
            "review_toggled": review_toggled,
            "review_deleted": review_deleted,
            "categories": CATEGORY_LABELS,
        },
    )


@app.post("/admin/reviews/toggle/{review_id}")
def admin_toggle_review(request: Request, review_id: str):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    reviews = load_reviews()
    for r in reviews:
        if r.get("id") == review_id:
            r["is_approved"] = not r.get("is_approved", True)
            break
    save_reviews(reviews)
    return RedirectResponse("/admin?review_toggled=1#reviews-section", status_code=303)


@app.post("/admin/reviews/delete/{review_id}")
def admin_delete_review(request: Request, review_id: str):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    reviews = load_reviews()
    reviews = [r for r in reviews if r.get("id") != review_id]
    save_reviews(reviews)
    return RedirectResponse("/admin?review_deleted=1#reviews-section", status_code=303)


@app.post("/admin/settings/save")
def admin_save_settings(
    request: Request,
    phone_display: str = Form(...),
    phone_raw: str = Form(...),
    whatsapp_greeting: str = Form(...),
    whatsapp_footer: str = Form(...),
    support_alias: str = Form(...),
    support_holder: str = Form(...),
):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    st = load_settings()
    st["phone_display"] = phone_display.strip()
    st["phone_raw"] = re.sub(r"[^0-9]+", "", phone_raw.strip())
    st["whatsapp_greeting"] = whatsapp_greeting.strip()
    st["whatsapp_footer"] = whatsapp_footer.strip()
    st["support_alias"] = support_alias.strip()
    st["support_holder"] = support_holder.strip()

    save_settings(st)
    return RedirectResponse("/admin?settings_saved=1", status_code=303)


@app.post("/admin/products/save")
async def admin_save_product(
    request: Request,
    id: str | None = Form(None),
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    portions: str | None = Form(""),
    badge: str | None = Form(""),
    description: str = Form(...),
    image_url: str | None = Form(None),
    image_file: UploadFile | None = File(None),
    is_featured: str | None = Form(None),
):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    products = load_products()
    existing = None
    if id:
        for p in products:
            if p.get("id") == id:
                existing = p
                break

    # Determinar imagen
    final_image = (
        existing.get("image")
        if existing
        else "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80"
    )

    # Si se subió un archivo nuevo
    if image_file and image_file.filename and len(image_file.filename.strip()) > 0:
        filename = image_file.filename.strip().lower()
        ext = Path(filename).suffix
        if not ext:
            ext = ".jpg"
        slug_base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        clean_name = f"{slug_base}-{int(time.time())}{ext}"
        upload_dir = BASE_DIR / "static" / "img" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / clean_name

        content = await image_file.read()
        if len(content) > 0:
            with open(file_path, "wb") as f:
                f.write(content)
            final_image = f"/static/img/uploads/{clean_name}"
    elif image_url and image_url.strip():
        final_image = image_url.strip()

    category_label = CATEGORY_LABELS.get(category, "Especialidades")
    is_feat_bool = is_featured in ("true", "1", "on")

    # Si se marca este producto como destacado en portada, desmarcar cualquier otro (exclusividad)
    if is_feat_bool:
        for p in products:
            p["is_featured"] = False

    if existing:
        existing["name"] = name.strip()
        existing["category"] = category
        existing["category_label"] = category_label
        existing["price"] = price
        existing["portions"] = portions.strip() if portions else ""
        existing["badge"] = badge.strip() if badge else ""
        existing["description"] = description.strip()
        existing["image"] = final_image
        existing["is_featured"] = is_feat_bool
    else:
        new_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or f"prod-{int(time.time())}"
        suffix = 1
        base_new_id = new_id
        while any(p.get("id") == new_id for p in products):
            new_id = f"{base_new_id}-{suffix}"
            suffix += 1

        new_product = {
            "id": new_id,
            "name": name.strip(),
            "category": category,
            "category_label": category_label,
            "badge": badge.strip() if badge else "",
            "description": description.strip(),
            "price": price,
            "portions": portions.strip() if portions else "",
            "image": final_image,
            "is_featured": is_feat_bool,
        }
        products.append(new_product)

    save_products(products)
    return RedirectResponse("/admin?saved=1", status_code=303)


@app.post("/admin/products/delete/{product_id}")
def admin_delete_product(request: Request, product_id: str):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    products = load_products()
    products = [p for p in products if p.get("id") != product_id]
    save_products(products)
    return RedirectResponse("/admin?deleted=1", status_code=303)
