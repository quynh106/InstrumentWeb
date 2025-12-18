from django.db import models
from products.models import Product
from django.contrib.auth.models import User

# Model để tracking inventory/stock changes
class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
        ('adjust', 'Adjust Stock'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.action} {self.quantity} units"

    class Meta:
        ordering = ['-created_at']
