from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product # Đảm bảo Product đã được import từ app 'products'

User = get_user_model()

class Order(models.Model):
    # Lựa chọn Trạng thái Đơn hàng (Cần khớp với STATUS_CHOICES trong views.py)
    STATUS_CHOICES = [
        ('Pending', 'Chờ xác nhận'),
        ('Confirmed', 'Đã xác nhận'),
        ('Shipping', 'Đang giao hàng'),
        ('Completed', 'Đã hoàn thành'),
        ('Canceled', 'Đã hủy'),
    ]
    
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, verbose_name="Khách hàng")
    total_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Trạng thái")
    
    # Thông tin nhận hàng (Có thể cần thêm model riêng cho Địa chỉ giao hàng thực tế)
    shipping_address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ giao hàng")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    def get_total_items(self):
        return self.items.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    # Lưu lại giá tại thời điểm mua để tránh thay đổi giá sau này
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tại thời điểm mua")

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"
        unique_together = ('order', 'product') # Không thể có 2 dòng cùng 1 sản phẩm trong 1 đơn

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase