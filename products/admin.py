from django.contrib import admin
from .models import Category, Brand, Product, Review, ProductImage,ReviewImage, FlashSale

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

# nhieu anh
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5 #admin sẽ hiển thị 5 ô trống để upload ảnh mới

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'brand', 'original_price', 'price', 'stock','image', 'created_at']
    list_filter = ['category', 'brand', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['original_price', 'price', 'stock','image']
    inlines = [ProductImageInline]
    list_display_links = ['id', 'name']  # ID và Name sẽ là link vào trang change
    list_per_page = 20

# nhieu anh
class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating','comment', 'sentiment', 'created_at']
    list_filter = ['rating', 'sentiment', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    inlines = [ReviewImageInline]
    list_per_page = 20


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = (
        "product", "flash_price",
        "start_time", "end_time",
        "is_active"
    )
    list_filter = ("is_active",)