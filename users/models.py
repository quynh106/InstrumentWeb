from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Liên kết 1-1 với tài khoản User mặc định của Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Các thông tin bổ sung cho khách mua nhạc cụ
    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ giao hàng")
    avatar = models.ImageField(upload_to='profile_pics', default='default.jpg', blank=True)

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Danh sách hồ sơ"
