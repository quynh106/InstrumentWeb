# products/urls.py

from django.urls import path
from . import views

# 🚨 DÒNG NÀY RẤT QUAN TRỌNG KHI DÙNG NAMESPACE 🚨
app_name = 'products' 

urlpatterns = [
    # 1. Trang Chủ Store (đường dẫn gốc)
    path('', views.home, name='home'), # Đã thêm dấu phẩy (,)

    # 2. Trang Danh sách Sản phẩm (đường dẫn rõ ràng hơn để tránh xung đột)
    # Tên 'product_list' được giữ lại để tương thích với link Products trong base.html
    path('list/', views.product_list, name='product_list'), 
    
    # 3. Trang Chi tiết Sản phẩm
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]