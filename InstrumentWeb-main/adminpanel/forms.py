from django import forms
from products.models import Product, Category, Brand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# Cần import Order Model nếu bạn muốn sử dụng OrderStatusUpdateForm
# from orders.models import Order 

User = get_user_model()

# --- 1. Form cho Sản phẩm (CRUD) ---
class ProductForm(forms.ModelForm):
    # Thêm các trường Image và Description để tùy chỉnh widget
    image = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'description', 'price', 'stock', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Tên Sản phẩm',
            'category': 'Danh mục',
            'brand': 'Hãng',
            'price': 'Giá bán',
            'stock': 'Tồn kho',
            'image': 'Ảnh',
            'is_available': 'Trạng thái bán',
        }

# --- 2. Form cho Danh mục (CRUD) ---
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # ĐÃ KHÔI PHỤC: Bao gồm 'slug' sau khi đã cập nhật Model Category và chạy migration
        fields = ['name', 'slug'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên Danh mục',
            'slug': 'Đường dẫn URL (Slug)',
        }

# --- 3. Form cho Hãng (CRUD) ---
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        # CẬP NHẬT: Thêm 'slug' để khớp với Model Brand đã sửa
        fields = ['name', 'slug'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên Hãng/Thương hiệu',
            'slug': 'Đường dẫn URL (Slug)',
        }

# --- 4. Form cho Quản lý Người dùng (Chỉnh sửa quyền) ---
class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Tên',
            'last_name': 'Họ',
            'email': 'Email',
            'is_active': 'Kích hoạt tài khoản',
            'is_staff': 'Quyền Admin/Staff',
        }

# --- 5. Form cho Cập nhật Trạng thái Đơn hàng ---
class OrderStatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ('Pending', 'Chờ xác nhận'),
        ('Confirmed', 'Đã xác nhận'),
        ('Shipping', 'Đang giao hàng'),
        ('Completed', 'Đã hoàn thành'),
        ('Canceled', 'Đã hủy'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )