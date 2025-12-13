from django.db import models
from django.contrib.auth.models import User

# Models Cart, CartItem đã được chuyển sang cart app
# Models Order, OrderItem đã được chuyển sang orders app
# Nếu cần thêm custom User profile, có thể định nghĩa ở đây

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
