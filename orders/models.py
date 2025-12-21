from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# 3. Đơn hàng
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # THÊM related_name ở đây:
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_from_orders_app')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

# 4. Item trong đơn hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # THÊM related_name ở đây:
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders_app_order_items')
    
    quantity = models.IntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.quantity * self.price_at_time