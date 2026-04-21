from rest_framework.viewsets import ModelViewSet

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.select_related('parent').prefetch_related('children')
