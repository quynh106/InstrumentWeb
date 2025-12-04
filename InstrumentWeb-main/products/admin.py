# InstrumentWeb-main/products/admin.py

from django.contrib import admin
# CHỈ IMPORT các Models thuộc ứng dụng PRODUCTS
from .models import Product, Category, Brand 

# Đăng ký các Model của ứng dụng Products
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)