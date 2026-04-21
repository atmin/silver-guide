from collections import deque
from typing import Any

import django_filters
from django.db.models import Q, QuerySet
from rest_framework.exceptions import NotFound

from .models import Category, Product


def _children_map(rows: list[Any]) -> dict[int, list[int]]:
    """Build a parent_id → [child_id, ...] map from a flat list of category rows."""
    cm: dict[int, list[int]] = {}
    for r in rows:
        cm.setdefault(r["parent_id"], []).append(r["id"])
    return cm


def _bfs(root_id: int, cm: dict[int, list[int]]) -> list[int]:
    """Return root_id plus all descendant IDs via breadth-first traversal of cm."""
    result: list[int] = []
    queue: deque[int] = deque([root_id])
    while queue:
        current = queue.popleft()
        result.append(current)
        queue.extend(cm.get(current, []))
    return result


def _descendant_ids_for_id(root_id: int) -> list[int]:
    rows = list(Category.objects.values("id", "parent_id"))
    return _bfs(root_id, _children_map(rows))


def _descendant_ids_for_slug(slug: str) -> list[int] | None:
    rows = list(Category.objects.values("id", "slug", "parent_id"))
    for r in rows:
        if r["slug"] == slug:
            return _bfs(r["id"], _children_map(rows))
    return None


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    sku = django_filters.CharFilter(lookup_expr="iexact")
    category_id = django_filters.NumberFilter(method="filter_category_id")
    category_slug = django_filters.CharFilter(method="filter_category_slug")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["q", "sku", "category_id", "category_slug", "price_min", "price_max"]

    def filter_q(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(Q(title__icontains=value) | Q(sku__icontains=value))

    def filter_category_id(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        if not Category.objects.filter(id=value).exists():
            raise NotFound(f"Category '{value}' not found.")
        return queryset.filter(category_id__in=_descendant_ids_for_id(value))

    def filter_category_slug(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        ids = _descendant_ids_for_slug(value)
        if ids is None:
            raise NotFound(f"Category '{value}' not found.")
        return queryset.filter(category_id__in=ids)
