import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "app" / "data"


def test_products_json_schema():
    products_path = BASE_DIR / "products.json"
    assert products_path.exists()
    with open(products_path, encoding="utf-8") as f:
        products = json.load(f)

    assert isinstance(products, list)
    assert len(products) >= 5

    required_keys = {"id", "name", "category", "price", "description", "image"}
    for p in products:
        missing = required_keys - set(p.keys())
        assert not missing, f"Product {p.get('id')} missing keys: {missing}"
        assert p["price"] > 0
        assert p["name"].strip()


def test_settings_json_schema():
    settings_path = BASE_DIR / "settings.json"
    assert settings_path.exists()
    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)

    assert isinstance(settings, dict)
    assert settings.get("support_alias") == "juarezdownes.tortas"
    assert "phone_display" in settings
    assert "phone_raw" in settings
    assert "whatsapp_greeting" in settings


def test_reviews_json_schema():
    reviews_path = BASE_DIR / "reviews.json"
    assert reviews_path.exists()
    with open(reviews_path, encoding="utf-8") as f:
        reviews = json.load(f)

    assert isinstance(reviews, list)
    assert len(reviews) > 0
    for r in reviews:
        assert "name" in r
        assert "comment" in r
        assert "rating" in r
        assert 1 <= r["rating"] <= 5
