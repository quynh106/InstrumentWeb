from django.contrib import admin
from .models import Order, OrderItem

# Class này giúp nhúng OrderItem vào trang chỉnh sửa Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Các trường chỉ đọc (readonly) để đảm bảo dữ liệu đơn hàng không bị thay đổi sau khi tạo
    readonly_fields = ['product', 'price_at_purchase', 'quantity'] 
    can_delete = False
    max_num = 0  # Ngăn thêm/xóa OrderItem từ Admin (chỉ dùng để hiển thị)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__email']
    
    # Nhúng OrderItemInline vào OrderAdmin
    inlines = [OrderItemInline]

# Đăng ký Model OrderItem riêng nếu cần quản lý độc lập
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price_at_purchase', 'quantity']
    list_filter = ['order__created_at']
    
    # Không cho phép chỉnh sửa trực tiếp các trường quan trọng
    readonly_fields = ['order', 'product', 'price_at_purchase', 'quantity']