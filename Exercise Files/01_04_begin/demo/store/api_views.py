from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView # RetrieveAPIView, UpdateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from store.serializers import ProductSerializer, ProductStatSerializer
from store.models import Product

class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id', )
    search_fields = ('product_name', 'description')

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

class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')

            if price is not None and float(price) <= 0.0:
                raise ValidationError({ 'price', 'Must be above $0.00'})

        except ValueError:
            raise ValidationError({ 'price': 'A valid number is required.'})

        return super().create(request, *args, **kwargs)

class ProductDestroy(DestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'

    # Overriding the delete method
    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)

        if response.status_code == 204:
            from django.core.cache import cache

            # all cache related to the product need to be cleared
            cache.delete(f'product_data_{product_id}')

        return response

class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer


    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)

        if response.status_code == 204:
            from django.core.cache import cache

            cache.delete(f'product_data_{product_id}')

        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            from django.core.cache import cache

            product = response.data

            # Adding product to cache
            cache.set(f"product_data_{product['id']}", {
                'product_name': product['product_name'],
                'description': product['description'],
                'price': product['price'],
            })

        return response

class ProductStats(GenericAPIView):
    lookup_field = 'id'
    serializer_class = ProductStatSerializer
    queryset = Product.objects.all()

    def get(self, reqquest, format=None, id=None):
        obj = self.get_object()
        serializer = ProductStatSerializer({
            'stats': {
                '2021-01-01': [5, 10, 15],
                '2021-01-02': [20, 1, 1],
            }
        })

        return Response(serializer.data)