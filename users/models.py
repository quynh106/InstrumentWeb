from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Thêm trường địa chỉ giao hàng
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    # Thêm trường số điện thoại
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
