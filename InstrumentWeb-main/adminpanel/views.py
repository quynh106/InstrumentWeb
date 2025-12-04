from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

# Import Models và Forms (Giả định Order/OrderItem đã tồn tại)
from products.models import Product, Category, Brand
from orders.models import Order, OrderItem # CẦN CÓ CÁC MODEL NÀY
from adminpanel.forms import ProductForm, CategoryForm, BrandForm, UserAdminForm, OrderStatusUpdateForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Kiểm tra quyền Admin/Staff
def is_admin_staff(user):
    return user.is_active and user.is_staff

# ------------------------------
# 1. DASHBOARD & THỐNG KÊ
# ------------------------------

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def admin_dashboard(request):
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 1. Doanh thu & Đơn hàng
    completed_orders = Order.objects.filter(status='Completed')
    
    monthly_revenue = completed_orders.filter(created_at__gte=start_of_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_revenue = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders_count = Order.objects.filter(status='Pending').count()
    
    # 2. Tồn kho
    total_stock = Product.objects.aggregate(Sum('stock'))['stock__sum'] or 0

    # 3. Sản phẩm bán chạy (Top 5)
    top_selling_items = OrderItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    # 4. Biểu đồ Doanh thu 7 ngày (Sử dụng Django ORM để lấy dữ liệu)
    # Lấy dữ liệu cho 7 ngày qua
    last_7_days = now - timedelta(days=7)
    revenue_data_query = completed_orders.filter(
        created_at__gte=last_7_days
    ).extra({'date': "date(created_at)"}).values('date').annotate(
        daily_revenue=Sum('total_amount')
    ).order_by('date')
    
    # Chuẩn bị dữ liệu cho Chart.js
    daily_revenue = {str(item['date']): item['daily_revenue'] for item in revenue_data_query}
    date_labels = []
    revenue_values = []
    
    # Điền giá trị 0 cho những ngày không có đơn hàng
    for i in range(7):
        date = (now - timedelta(days=i)).date()
        date_str = str(date)
        date_labels.insert(0, date.strftime('%d/%m')) # Nhãn ngày
        revenue_values.insert(0, daily_revenue.get(date_str, 0)) # Doanh thu

    context = {
        'title': 'Dashboard Quản trị',
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders_count,
        'total_stock': total_stock,
        'top_selling_items': top_selling_items,
        'revenue_chart_labels': date_labels,
        'revenue_chart_data': revenue_values,
    }
    return render(request, 'adminpanel/dashboard.html', context)


# ------------------------------
# 2. CRUD SẢN PHẨM (Code đã cung cấp)
# ------------------------------

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def product_list(request):
    products = Product.objects.all().select_related('category', 'brand')
    context = {'title': 'Quản lý Sản phẩm', 'products': products}
    return render(request, 'adminpanel/product_list.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được thêm thành công.')
            return redirect('adminpanel:product_list')
    else:
        form = ProductForm()
    
    context = {'title': 'Thêm Sản phẩm Mới', 'form': form}
    return render(request, 'adminpanel/product_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sản phẩm "{product.name}" đã được cập nhật.')
            return redirect('adminpanel:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {'title': 'Chỉnh sửa Sản phẩm', 'form': form}
    return render(request, 'adminpanel/product_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Sản phẩm "{product.name}" đã được xóa.')
        return redirect('adminpanel:product_list')
    
    context = {'title': 'Xóa Sản phẩm', 'item': product}
    return render(request, 'adminpanel/confirm_delete.html', context)


# ------------------------------
# 3. CRUD DANH MỤC & HÃNG (Hoàn thiện)
# ------------------------------

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def category_list(request):
    categories = Category.objects.all()
    context = {'title': 'Quản lý Danh mục', 'categories': categories}
    return render(request, 'adminpanel/category_list.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được thêm thành công.')
            return redirect('adminpanel:category_list')
    else:
        form = CategoryForm()
    context = {'title': 'Thêm Danh mục Mới', 'form': form}
    return render(request, 'adminpanel/category_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Danh mục "{category.name}" đã được cập nhật.')
            return redirect('adminpanel:category_list')
    else:
        form = CategoryForm(instance=category)
    context = {'title': 'Chỉnh sửa Danh mục', 'form': form}
    return render(request, 'adminpanel/category_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Danh mục "{category.name}" đã được xóa.')
        return redirect('adminpanel:category_list')
    context = {'title': 'Xóa Danh mục', 'item': category}
    return render(request, 'adminpanel/confirm_delete.html', context)

# Hãng/Thương hiệu
@login_required
@user_passes_test(is_admin_staff, login_url='/')
def brand_list(request):
    brands = Brand.objects.all()
    context = {'title': 'Quản lý Hãng', 'brands': brands}
    return render(request, 'adminpanel/brand_list.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def brand_add(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hãng đã được thêm thành công.')
            return redirect('adminpanel:brand_list')
    else:
        form = BrandForm()
    context = {'title': 'Thêm Hãng Mới', 'form': form}
    return render(request, 'adminpanel/brand_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hãng "{brand.name}" đã được cập nhật.')
            return redirect('adminpanel:brand_list')
    else:
        form = BrandForm(instance=brand)
    context = {'title': 'Chỉnh sửa Hãng', 'form': form}
    return render(request, 'adminpanel/brand_form.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, f'Hãng "{brand.name}" đã được xóa.')
        return redirect('adminpanel:brand_list')
    context = {'title': 'Xóa Hãng', 'item': brand}
    return render(request, 'adminpanel/confirm_delete.html', context)

# ------------------------------
# 4. QUẢN LÝ ĐƠN HÀNG & LOGIC KHO
# ------------------------------

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def order_list(request):
    orders = Order.objects.all().order_by('-created_at').select_related('user')
    context = {'title': 'Quản lý Đơn hàng', 'orders': orders}
    return render(request, 'adminpanel/order_list.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
@transaction.atomic # Đảm bảo giao dịch an toàn (update kho và status)
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    # Định nghĩa các lựa chọn trạng thái để truyền vào template
    order_status_choices = OrderStatusUpdateForm.STATUS_CHOICES 

    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = order.status
        
        if old_status != new_status:
            try:
                # Logic QUẢN LÝ KHO khi thay đổi trạng thái
                
                # 1. Hoàn kho nếu bị HỦY (Chỉ khi Hủy từ trạng thái chưa Hoàn thành)
                if new_status == 'Canceled' and old_status not in ['Completed', 'Canceled']:
                    for item in order_items:
                        product = item.product
                        product.stock = F('stock') + item.quantity
                        product.save()
                    messages.warning(request, f'Đơn hàng #{pk} đã bị HỦY. Đã hoàn lại sản phẩm vào tồn kho.')
                
                # 2. Trừ kho khi XÁC NHẬN (Chỉ khi chuyển từ Pending sang Confirmed)
                elif new_status == 'Confirmed' and old_status == 'Pending':
                    # Kiểm tra và trừ kho (bước quan trọng)
                    for item in order_items:
                        product = item.product
                        if product.stock < item.quantity:
                            # Nếu không đủ kho, hủy giao dịch và thông báo lỗi
                            raise ValueError(f'Không đủ tồn kho cho sản phẩm: {product.name}')
                        product.stock = F('stock') - item.quantity
                        product.save()
                    messages.success(request, f'Đơn hàng #{pk} đã được XÁC NHẬN. Đã trừ sản phẩm khỏi tồn kho.')

                # Cập nhật trạng thái Order cuối cùng
                order.status = new_status
                order.updated_at = timezone.now()
                order.save()
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Lỗi khi cập nhật trạng thái: {e}')
            
            return redirect('adminpanel:order_detail', pk=pk)

    context = {
        'title': f'Chi tiết Đơn hàng #{order.id}',
        'order': order,
        'order_items': order_items,
        'order_status_choices': order_status_choices,
    }
    return render(request, 'adminpanel/order_detail.html', context)


# 5. QUẢN LÝ TÀI KHOẢN (ROLE ADMIN)


@login_required
@user_passes_test(is_admin_staff, login_url='/')
def user_management(request):
    # Lấy tất cả người dùng trừ người dùng hiện tại (Admin đang đăng nhập)
    users = User.objects.exclude(id=request.user.id).order_by('username')
    context = {'title': 'Quản lý Tài khoản', 'users': users}
    return render(request, 'adminpanel/user_management.html', context)

@login_required
@user_passes_test(is_admin_staff, login_url='/')
def user_edit(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Sử dụng UserAdminForm để chỉnh sửa thông tin và quyền hạn
        form = UserAdminForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tài khoản "{user_to_edit.username}" đã được cập nhật quyền.')
            return redirect('adminpanel:user_management')
    else:
        form = UserAdminForm(instance=user_to_edit)
        
    context = {'title': f'Chỉnh sửa Quyền: {user_to_edit.username}', 'user_to_edit': user_to_edit, 'form': form}
    return render(request, 'adminpanel/user_edit_form.html', context)