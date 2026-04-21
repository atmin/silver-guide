from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from core.filters import StrictDjangoFilterBackend
from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.select_related("parent").prefetch_related("children")


@extend_schema(
    parameters=[
        OpenApiParameter(
            "q",
            OpenApiTypes.STR,
            description="Search by title or SKU substring (case-insensitive).",
        ),
        OpenApiParameter(
            "sku", OpenApiTypes.STR, description="Exact SKU match (case-insensitive)."
        ),
        OpenApiParameter(
            "category_id",
            OpenApiTypes.INT,
            description="Return products in this category and all its descendants.",
        ),
        OpenApiParameter(
            "category_slug",
            OpenApiTypes.STR,
            description="Same as category_id but accepts a category slug instead of a numeric ID.",
        ),
        OpenApiParameter(
            "price_min", OpenApiTypes.DECIMAL, description="Minimum price (inclusive)."
        ),
        OpenApiParameter(
            "price_max", OpenApiTypes.DECIMAL, description="Maximum price (inclusive)."
        ),
        OpenApiParameter(
            "ordering",
            OpenApiTypes.STR,
            description="Sort field. Prefix with `-` for descending. Allowed: `price`, `created_at`, `title`.",
        ),
    ]
)
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [StrictDjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["price", "created_at", "title"]
    ordering = ["title"]

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
