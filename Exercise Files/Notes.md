# Store API

### View Products
http://localhost:8000/api/v1/products/

### Create Products
```
curl -X POST http://localhost:8000/api/v1/products/new -d price=1.00 -d name='My Product' -d description='Hello World'
```