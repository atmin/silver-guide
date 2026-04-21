from django.db.models import QuerySet
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.views import APIView

# Query params that are not filter fields and should not trigger "unknown param" errors
_RESERVED_PARAMS = {"ordering", "page", "page_size", "cursor", "format"}


class StrictDjangoFilterBackend(DjangoFilterBackend):
    """Raises 400 on unknown filter parameters and on invalid filter values."""

    def filter_queryset(
        self, request: HttpRequest, queryset: QuerySet, view: APIView
    ) -> QuerySet:
        assert isinstance(request, Request)
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        unknown = (
            set(request.query_params) - set(filterset.filters) - _RESERVED_PARAMS
        )
        if unknown:
            raise ValidationError(
                {param: "Unknown filter parameter." for param in sorted(unknown)}
            )

        if not filterset.is_valid():
            raise ValidationError(filterset.errors)

        return filterset.qs
