from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)#giá gốc
    price = models.DecimalField(max_digits=10, decimal_places=2)#giá bán
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(days=14)
    
    @property
    def discount_percent(self):
        if self.original_price and self.price < self.original_price:
            return round(
                (self.original_price - self.price) / self.original_price * 100
            )
        return 0
    
    def get_filtered_products(search='', category_id=None, brand_id=None):
        qs = Product.objects.all()
        if search:
            qs = qs.filter(name__icontains=search)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        return qs
    
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/images/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} image"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    SENTIMENT_CHOICES = (
        ("positive", "Positive"),
        ("neutral", "Neutral"),
        ("negative", "Negative"),
    )
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        default="neutral"
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/reviews/")




class FlashSale(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="flash_sales"
    )
    flash_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    quantity = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_running(self):
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time and self.sold < self.quantity


    def discount_percent(self):
        if self.product.original_price:
            return round(
                (self.product.original_price - self.flash_price)
                / self.product.original_price * 100
            )

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Thời gian không hợp lệ")

        if self.flash_price >= self.product.original_price:
            raise ValidationError("Giá flash sale phải thấp hơn giá gốc")

        if self.quantity > self.product.stock:
            raise ValidationError("Số lượng flash sale vượt tồn kho")

        qs = FlashSale.objects.filter(
            product=self.product,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError("Flash sale bị trùng hoặc lồng thời gian")

    def __str__(self):
        return f"FlashSale {self.product.name}"

