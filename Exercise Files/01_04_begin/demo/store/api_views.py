from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from store.serializers import ProductSerializer
from store.models import Product

class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('id', )

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)

        queryset = Product.objects.all()

        from django.utils import timezone
        now = timezone.now()

        if on_sale is None:
            return super().get_queryset()

        elif on_sale.lower() == 'true':
            return queryset.filter(
                sale_start__lte = now,
                sale_end__gte = now,
            )

        elif on_sale.lower() == 'false':
            return queryset.filter(
                sale_start__lt = now,
                sale_end__lt = now,
            )

        else:
            return queryset