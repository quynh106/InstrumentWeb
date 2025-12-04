from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.db.models import Q 

# --- 1. Category và Brand ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # TRƯỜNG SLUG ĐÃ THÊM
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Tự động tạo slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # TRƯỜNG SLUG ĐÃ THÊM
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Tự động tạo slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# --- 2. Product (Sản phẩm) ---
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='products')
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    image = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def get_filtered_products(q=None, category_id=None, brand_id=None):
        """Lấy danh sách sản phẩm được lọc theo từ khóa, danh mục và hãng."""
        queryset = Product.objects.filter(is_available=True)

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        return queryset.order_by('-created_at')