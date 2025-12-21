from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Order Management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),

    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:product_id>/update/', views.inventory_update, name='inventory_update'),

    # Statistics
    path('statistics/', views.statistics, name='statistics'),
]
