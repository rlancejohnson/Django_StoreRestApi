from rest_framework.test import APITestCase
from store.models import Product

class ProductCreateTestCase(APITestCase):
    def test_create_product(self):
        initial_product_count = Product.objects.count()
        product_attrs = {
            'product_name': 'New Product',
            'description': 'Awesaome Product',
            'price': '123.45',
        }

        response = self.client.post('/api/v1/products/new', product_attrs)
        if response.status_code != 201:
            print(response.data)

        self.assertEqual(
            Product.objects.count(),
            initial_product_count + 1,
        )

        for attr, expected_value in product_attrs.items():
            self.assertEqual(response.data[attr], expected_value)

        self.assertEqual(response.data['is_on_sale'], False)

        self.assertEqual(
            response.data['current_price'],
            float(product_attrs['price']),
        )

class ProductDestroyTestCase(APITestCase):
    def test_delete_product(self):
        initial_product_count = Product.objects.count()
        product_id = Product.objects.first().id
        self.client.delete(f'/api/v1/products/{product_id}/')

        self.assertEqual(
            Product.objects.count(),
            initial_product_count - 1,
        )

        self.assertRaises(
            Product.DoesNotExist,
            Product.objects.get,
            id=product_id,
        )

class ProductListTestCase(APITestCase):
    def test_list_products(self):
        products_count = Product.objects.count()
        response = self.client.get('/api/v1/products/')

        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['count'], products_count)
        self.assertEqual(len(response.data['results']), products_count)

class ProductUpdateTestCase(APITestCase):
    def test_update_product(self):
        product = Product.objects.first()

        response = self.client.patch(f'/api/v1/products/{product.id}/', {
            'product_name': 'New Product',
            'description': 'Awesome Product',
            'price': 123.45,
        }, format='json')

        updated = Product.objects.get(id=product.id)

        self.assertEqual(updated.name, 'New Product')
