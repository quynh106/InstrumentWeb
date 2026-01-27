from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # --- Dashboard Chính ---
    path('', views.dashboard, name='dashboard'),

    # --- Quản lý đơn hàng (Order Management) ---
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),

    # --- Quản lý kho hàng (Inventory Management) ---
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:product_id>/update/', views.inventory_update, name='inventory_update'),

    # --- Thống kê báo cáo (Statistics) ---
    path('statistics/', views.statistics, name='statistics'),
    
    # THÊM DÒNG NÀY VÀO ĐÂY:
    path('export-orders-csv/', views.export_orders_csv, name='export_orders_csv'),
    # --- PHÂN TÍCH CẢM XÚC & PHẢN HỒI (Sentiment Intelligence) ---
    # Trang dashboard hiển thị các biểu đồ và danh sách đánh giá
    path('sentiment/', views.sentiment_analytics, name='sentiment_analytics'),
    
]