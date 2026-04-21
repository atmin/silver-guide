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
