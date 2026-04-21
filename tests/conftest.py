import pytest
from rest_framework.test import APIClient

from catalog.models import Category, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category_tree():
    root = Category.objects.create(name="Хранителни стоки", slug="hrani")
    child = Category.objects.create(
        name="Млечни продукти", slug="hrani-mlechni", parent=root
    )
    grandchild = Category.objects.create(
        name="Сирена", slug="hrani-mlechni-sirena", parent=child
    )
    return {"root": root, "child": child, "grandchild": grandchild}


@pytest.fixture
def products(category_tree):
    root = category_tree["root"]
    child = category_tree["child"]
    grandchild = category_tree["grandchild"]

    return [
        Product.objects.create(
            sku="PRD-001", title="Прясно мляко", price="1.99", category=child
        ),
        Product.objects.create(
            sku="PRD-002", title="Кисело мляко", price="1.49", category=child
        ),
        Product.objects.create(
            sku="SIR-001", title="Бяло сирене", price="3.99", category=grandchild
        ),
        Product.objects.create(
            sku="SIR-002", title="Кашкавал", price="4.49", category=grandchild
        ),
        Product.objects.create(
            sku="HRA-001", title="Хляб Добруджа", price="1.39", category=root
        ),
        Product.objects.create(
            sku="HRA-INACTIVE",
            title="Стар продукт",
            price="0.99",
            category=root,
            is_active=False,
        ),
    ]
