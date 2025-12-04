# users/urls.py

from django.urls import path
from . import views

app_name = 'account' # Khớp với LOGIN_URL = 'account:login'

urlpatterns = [
    path('login/', views.user_login, name='login'), # Trỏ đến hàm user_login
    # Bạn có thể thêm logout sau này
    # path('logout/', views.user_logout, name='logout'),
]