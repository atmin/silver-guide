from collections import deque

import django_filters
from django.db.models import Q, QuerySet

from .models import Category, Product


def _descendant_ids(root_id: int) -> list[int]:
    """BFS over all categories in memory, returns root_id plus all descendant IDs."""
    all_categories = list(Category.objects.values("id", "parent_id"))
    children_map: dict[int, list[int]] = {}
    for cat in all_categories:
        children_map.setdefault(cat["parent_id"], []).append(cat["id"])

    result: list[int] = []
    queue: deque[int] = deque([root_id])
    while queue:
        current = queue.popleft()
        result.append(current)
        queue.extend(children_map.get(current, []))
    return result


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
        return queryset.filter(category_id__in=_descendant_ids(value))

    def filter_category_slug(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        try:
            root_id = Category.objects.values_list("id", flat=True).get(slug=value)
        except Category.DoesNotExist:
            return queryset.none()
        return queryset.filter(category_id__in=_descendant_ids(root_id))
