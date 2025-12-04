from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # ------------------ Quản lý Sản phẩm (CRUD) ------------------
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # ------------------ Quản lý Danh mục (CRUD) ------------------
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # ------------------ Quản lý Hãng (CRUD) ------------------
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_add, name='brand_add'),
    path('brands/edit/<int:pk>/', views.brand_edit, name='brand_edit'),
    path('brands/delete/<int:pk>/', views.brand_delete, name='brand_delete'),
    
    # ------------------ Quản lý Đơn hàng (List & Update Status) ------------------
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # ------------------ Quản lý Tài khoản (User Management) ------------------
    path('users/', views.user_management, name='user_management'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
]