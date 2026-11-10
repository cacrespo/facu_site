from fastapi.testclient import TestClient

from app.main import app, get_admin_token, load_products, load_reviews, save_products, save_reviews

client = TestClient(app)


def test_home_page():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Juárez Downes" in resp.text
    assert "Mis Delicias Artesanales" in resp.text
    assert "El cariño del barrio" in resp.text
    assert "juarezdownes.tortas" in resp.text


def test_head_request():
    resp = client.head("/")
    assert resp.status_code == 200


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_get_products_list():
    resp = client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) > 0
    rogel = next((p for p in products if p["id"] == "rogel-clasico"), None)
    assert rogel is not None
    assert rogel["price"] > 0


def test_get_products_by_category():
    resp = client.get("/api/products?category=tartas")
    assert resp.status_code == 200
    products = resp.json()
    for p in products:
        assert p["category"] == "tartas"


def test_get_single_product_not_found():
    resp = client.get("/api/products/producto-inexistente-12345")
    assert resp.status_code == 404


def test_reviews_api():
    resp = client.get("/api/reviews")
    assert resp.status_code == 200
    reviews = resp.json()
    assert isinstance(reviews, list)
    assert len(reviews) > 0


def test_submit_review():

    initial_reviews = load_reviews()
    try:
        payload = {
            "name": "Cliente de Prueba",
            "neighborhood": "Hurlingham",
            "rating": 5,
            "comment": "Torta riquísima para el festejo",
        }
        resp = client.post("/api/reviews", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["review"]["name"] == "Cliente de Prueba"
    finally:
        save_reviews(initial_reviews)


def test_whatsapp_link_builder():
    payload = {
        "items": [
            {
                "id": "rogel-clasico",
                "name": "Rogel Clásico Tradicional",
                "quantity": 1,
                "price": 18500,
            }
        ],
        "customer_name": "Laura",
        "delivery_type": "Entrega en Hurlingham",
        "notes": "Para el domingo",
    }
    resp = client.post("/api/orders/whatsapp-link", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "https://wa.me/" in data["url"]
    assert "Laura" in data["message"]


def test_admin_auth_flow():
    # Login page GET
    resp = client.get("/admin/login")
    assert resp.status_code == 200

    # Wrong password -> 401
    resp_bad = client.post("/admin/login", data={"password": "wrong-password"})
    assert resp_bad.status_code == 401

    # Unauthenticated access to /admin -> Redirect to /admin/login
    resp_unauth = client.get("/admin", follow_redirects=False)
    assert resp_unauth.status_code == 303
    assert "/admin/login" in resp_unauth.headers["location"]

    # Authenticated access to /admin with cookie
    client.cookies.set("admin_session", get_admin_token())
    resp_auth = client.get("/admin")
    assert resp_auth.status_code == 200
    assert "Panel de Catálogo" in resp_auth.text


def test_featured_product_exclusivity():
    initial_products = load_products()
    client.cookies.set("admin_session", get_admin_token())
    try:
        # Mark tarta-ricota as featured
        resp = client.post(
            "/admin/products/save",
            data={
                "id": "tarta-ricota",
                "name": "Tarta de Ricota Tradicional",
                "category": "tartas",
                "price": "14000",
                "portions": "8 porciones",
                "badge": "",
                "description": "Relleno cremoso y suave aromatizado con limón",
                "is_featured": "true",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

        # Verify only tarta-ricota is featured
        products = load_products()
        featured = [p for p in products if p.get("is_featured")]
        assert len(featured) == 1
        assert featured[0]["id"] == "tarta-ricota"

        # Verify home page renders this product in the hero section
        resp_home = client.get("/")
        assert resp_home.status_code == 200
        assert "Tarta de Ricota Tradicional" in resp_home.text
    finally:
        save_products(initial_products)
