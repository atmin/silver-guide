from collections import deque
from typing import Any

import django_filters
from django.db.models import Q, QuerySet
from rest_framework.exceptions import NotFound

from .models import Category, Product


def _parent_children(rows: list[Any]) -> dict[int, list[int]]:
    """Build a parent_id → [child_id, ...] map from a flat list of rows."""
    cm: dict[int, list[int]] = {}
    for r in rows:
        cm.setdefault(r["parent_id"], []).append(r["id"])
    return cm


def _breadth_first_traversal(
    from_id: int, parent_children: dict[int, list[int]]
) -> list[int]:
    """Return from_id plus all descendant IDs via breadth-first traversal of parent_children."""
    result: list[int] = []
    queue: deque[int] = deque([from_id])
    while queue:
        current = queue.popleft()
        result.append(current)
        queue.extend(parent_children.get(current, []))
    return result


def _descendants_for_id(for_id: int) -> list[int] | None:
    rows = list(Category.objects.values("id", "parent_id"))
    for r in rows:
        if r["id"] == for_id:
            return _breadth_first_traversal(r["id"], _parent_children(rows))
    return None


def _descendants_for_slug(for_slug: str) -> list[int] | None:
    rows = list(Category.objects.values("id", "slug", "parent_id"))
    for r in rows:
        if r["slug"] == for_slug:
            return _breadth_first_traversal(r["id"], _parent_children(rows))
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
        ids = _descendants_for_id(value)
        if ids is None:
            raise NotFound(f"Category '{value}' not found.")
        return queryset.filter(category_id__in=ids)

    def filter_category_slug(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        ids = _descendants_for_slug(value)
        if ids is None:
            raise NotFound(f"Category '{value}' not found.")
        return queryset.filter(category_id__in=ids)
