from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn cho trang Đăng ký: http://127.0.0.1:8000/users/register/
    path('register/', views.register, name='register'),
    
    # Đường dẫn cho trang Đăng nhập: http://127.0.0.1:8000/users/login/
    path('login/', views.login_view, name='login'),
    
    # Đường dẫn cho trang Đăng xuất: http://127.0.0.1:8000/users/logout/
    path('logout/', views.logout_view, name='logout'),
]
