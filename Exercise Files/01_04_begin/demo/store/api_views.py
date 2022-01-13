from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from store.serializers import ProductSerializer
from store.models import Product

class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id', )
    search_fields = ('name', 'description')

    pagination_class = ProductsPagination

    def getQueryset(self):
        return self.queryset

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)

        queryset = self.getQueryset()

        from django.utils import timezone
        now = timezone.now()

        if on_sale is not None and on_sale.lower() == 'true':
            return queryset.filter(
                sale_start__lte = now,
                sale_end__gte = now,
            )

        elif on_sale is not None and on_sale.lower() == 'false':
            return queryset.filter(
                sale_start__lt = now,
                sale_end__lt = now,
            )

        else:
            return queryset