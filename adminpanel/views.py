from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import HttpResponse
import json
import csv

# =================================================================
# IMPORT MODELS - HỆ THỐNG QUẢN TRỊ TỔNG THỂ
# =================================================================
from orders.models import Order, OrderItem
from products.models import Product, Category, Brand, Review
from .models import InventoryLog

# =================================================================
# PHẦN 0: CÁC HÀM BỔ TRỢ & DECORATORS PHÂN QUYỀN
# =================================================================

def is_admin(user):
    """
    Phân quyền nghiêm ngặt: Chỉ Staff hoặc Superuser mới có quyền truy cập.
    """
    return user.is_active and (user.is_staff or user.is_superuser)

def calculate_growth(current, previous):
    """
    Hàm tính toán tỷ lệ tăng trưởng phần trăm giữa hai kỳ báo cáo.
    """
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 2)

# =================================================================
# PHẦN 1: DASHBOARD - TRUNG TÂM ĐIỀU HÀNH CHIẾN LƯỢC
# =================================================================

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    View tổng hợp toàn bộ KPI kinh doanh, doanh thu và hiệu suất bán hàng.
    Đã sửa lỗi lọc Status để hiển thị dữ liệu ngay lập tức.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)

        # 1. Khởi tạo danh sách trạng thái hợp lệ dựa trên Model của bạn
    # Bao gồm 'pending' để chắc chắn dữ liệu mẫu (mock data) hiện lên
    valid_statuses = ['pending', 'paid', 'shipped', 'completed']

    # 2. Lấy dữ liệu cơ sở (Base Query)
    orders_query = Order.objects.filter(status__in=valid_statuses)

    # 3. Áp dụng bộ lọc ngày (nếu người dùng có chọn trên giao diện)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    if start_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date)
    if end_date:
        orders_query = orders_query.filter(created_at__date__lte=end_date)

    # 4. Thống kê Quick Stats (Dựa trên orders_query đã lọc ngày)
    total_orders = orders_query.count()
    total_revenue = orders_query.aggregate(total=Sum('total_price'))['total'] or 0

    # Các thông số khác không phụ thuộc vào bộ lọc ngày (Tổng quan hệ thống)
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
        # 1.2. Phân tích doanh thu biến động trong 7 ngày qua
    recent_revenue_data = Order.objects.filter(
    created_at__gte=seven_days_ago,
    status__in=['paid', 'shipped', 'completed'] # Đã định nghĩa trực tiếp
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # 1.3. Lấy dữ liệu danh sách hiển thị (Table Data)
    # Tối ưu SQL bằng select_related để lấy thông tin khách hàng trong 1 lần query
    recent_orders = Order.objects.all().select_related('user').order_by('-created_at')[:10]
    
    # Top 5 sản phẩm bán chạy nhất (Dựa trên số lượng thực tế trong đơn hàng)
    top_products = Product.objects.annotate(
        total_sold=Sum('orders_app_order_items__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

    # 1.4. Chuẩn bị dữ liệu biểu đồ phân tích danh mục (Chart.js Data)
    # Lấy dữ liệu phân bổ doanh số theo ngành hàng
    categories_stats = Category.objects.annotate(
        total_qty=Sum('products__orders_app_order_items__quantity')
    ).filter(total_qty__gt=0).order_by('-total_qty')[:6]

    cat_labels = [c.name for c in categories_stats]
    cat_values = [int(c.total_qty or 0) for c in categories_stats]

    # 1.5. Đóng gói Context truyền ra Template Admin
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_revenue': recent_revenue_data,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'cat_labels': cat_labels,
        'cat_sold': cat_values,
        'cat_labels_js': json.dumps(cat_labels),
        'cat_sold_js': json.dumps(cat_values),
        'current_time': now,
        'page_title': "Bảng điều khiển hệ thống quản trị"
    }
    return render(request, 'adminpanel/dashboard.html', context)

# =================================================================
# PHẦN 2: QUẢN LÝ ĐƠN HÀNG (ORDER MANAGEMENT SYSTEM)
# =================================================================

@login_required
@user_passes_test(is_admin)
def order_list(request):
    """
    Quản lý và bộ lọc danh sách đơn hàng toàn diện.
    """
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    date_sort = request.GET.get('sort', '-created_at')
    
    orders = Order.objects.all().select_related('user')

    # Thực hiện lọc theo yêu cầu từ giao diện
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) | 
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    orders = orders.order_by(date_sort)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_results': orders.count(),
        'page_title': "Danh sách đơn hàng"
    }
    return render(request, 'adminpanel/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """
    Xem chi tiết từng mặt hàng trong đơn hàng và thông tin khách hàng.
    """
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all().select_related('product')
    
    context = {
        'order': order,
        'items': order_items,
        'page_title': f"Chi tiết đơn hàng #{order.id}"
    }
    return render(request, 'adminpanel/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def order_update_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Cập nhật danh sách này khớp 100% với các value trong thẻ <option> của HTML
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
        
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"Đơn hàng #{order.id} đã chuyển sang: {new_status.upper()}")
        else:
            messages.error(request, f"Lỗi: Trạng thái '{new_status}' không nằm trong danh mục cho phép.")
            
    return redirect('adminpanel:order_detail', order_id=order_id)

# =================================================================
# PHẦN 3: QUẢN LÝ KHO HÀNG (INVENTORY & LOGISTICS)
# =================================================================

@login_required
@user_passes_test(is_admin)
def inventory_list(request):
    """
    Theo dõi tồn kho sản phẩm, cảnh báo hàng sắp hết.
    """
    query = request.GET.get('q', '')
    brand_id = request.GET.get('brand', '')
    
    products = Product.objects.all().select_related('category', 'brand')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    
    if brand_id:
        products = products.filter(brand_id=brand_id)

    # Ưu tiên các mặt hàng sắp hết kho lên trên cùng
    products = products.order_by('stock')

    context = {
        'products': products,
        'search_query': query,
        'brands': Brand.objects.all(),
        'page_title': "Quản lý kho hàng"
    }
    return render(request, 'adminpanel/inventory_list.html', context)

@login_required
@user_passes_test(is_admin)
def inventory_update(request, product_id):
    """
    Cập nhật số lượng kho và ghi log chi tiết để đối soát sau này.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        action_type = request.POST.get('action') # add, remove, adjust
        try:
            quantity_input = int(request.POST.get('quantity', 0))
            if quantity_input < 0: raise ValueError
        except ValueError:
            messages.error(request, "Lỗi: Số lượng nhập vào phải là số dương.")
            return redirect('adminpanel:inventory_update', product_id=product_id)
            
        reason = request.POST.get('notes', 'Cập nhật định kỳ từ Admin')
        prev_stock = product.stock

        if action_type == 'add':
            product.stock += quantity_input
        elif action_type == 'remove':
            product.stock = max(0, product.stock - quantity_input)
        elif action_type == 'adjust':
            product.stock = quantity_input
        
        product.save()

        # Ghi nhật ký kho hàng (Rất quan trọng để theo vết lỗi)
        InventoryLog.objects.create(
            product=product,
            action=action_type,
            quantity=quantity_input,
            previous_stock=prev_stock,
            new_stock=product.stock,
            notes=reason,
            created_by=request.user
        )
        
        messages.success(request, f"Đã cập nhật tồn kho cho: {product.name}")
        return redirect('adminpanel:inventory_list')

    return render(request, 'adminpanel/inventory_update.html', {'product': product})

# =================================================================
# PHẦN 4: THỐNG KÊ, BÁO CÁO & XUẤT DỮ LIỆU (REPORTING)
# =================================================================

from decimal import Decimal
from django.db.models import Sum, F, Q

@login_required
@user_passes_test(is_admin)
def statistics(request):
    """
    Báo cáo tài chính fix lỗi FieldError và TypeError.
    Sử dụng chính xác price_at_time và orders_app_order_items.
    """
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # 1. Lọc đơn hàng theo trạng thái và ngày tháng
    revenue_statuses = ['paid', 'shipped', 'delivered', 'completed']
    orders_query = Order.objects.filter(status__in=revenue_statuses)
    
    if start_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date)
    if end_date:
        orders_query = orders_query.filter(created_at__date__lte=end_date)

    # Lấy danh sách ID để tối ưu hóa join
    filtered_order_ids = orders_query.values_list('id', flat=True)

    # 2. Hiệu suất theo Brand
    # Lưu ý: price_at_time là trường trong OrderItem của bạn
    brand_performance = Brand.objects.annotate(
        items_sold=Sum(
            'products__orders_app_order_items__quantity', 
            filter=Q(products__orders_app_order_items__order_id__in=filtered_order_ids)
        ),
        total_rev=Sum(
            F('products__orders_app_order_items__quantity') * F('products__orders_app_order_items__price_at_time'),
            filter=Q(products__orders_app_order_items__order_id__in=filtered_order_ids)
        )
    ).filter(items_sold__gt=0).order_by('-total_rev')

    # 3. Tính toán doanh thu thực tế (Actual Revenue)
    actual_revenue = orders_query.aggregate(s=Sum('total_price'))['s'] or Decimal('0.00')
    
    # 4. Tính toán Discount Impact (Thiệt hại do giảm giá)
    total_potential_revenue = Decimal('0.00')
    delivered_items = OrderItem.objects.filter(order_id__in=filtered_order_ids).select_related('product')
    
    for item in delivered_items:
        # Lấy giá gốc (original_price) từ Product model nếu có, nếu không lấy giá niêm yết hiện tại
        orig_price = getattr(item.product, 'original_price', item.product.price) or item.product.price
        total_potential_revenue += (Decimal(str(orig_price)) * item.quantity)

    # Fix lỗi TypeError bằng cách ép kiểu Decimal đồng nhất
    discount_loss = total_potential_revenue - Decimal(str(actual_revenue))

    context = {
        'brand_performance': brand_performance,
        'actual_revenue': actual_revenue,
        'discount_loss': max(Decimal('0.00'), discount_loss),
        'total_delivered': len(filtered_order_ids),
        'page_title': "Báo cáo thống kê tài chính",
        'now': timezone.now()
    }
    return render(request, 'adminpanel/statistics.html', context)

@login_required
@user_passes_test(is_admin)
def export_orders_csv(request):
    """
    Xuất báo cáo đơn hàng ra file CSV phục vụ kế toán.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Full_Orders_Report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer Username', 'Email', 'Total Price', 'Status', 'Created At'])
    
    orders = Order.objects.all().select_related('user')
    for o in orders:
        writer.writerow([o.id, o.user.username, o.user.email, o.total_price, o.status, o.created_at])
        
    return response

# =================================================================
# PHẦN 5: SENTIMENT ANALYTICS - PHÂN TÍCH TRÍ TUỆ CẢM XÚC AI
# =================================================================

@login_required
@user_passes_test(is_admin)
def sentiment_analytics(request):
    """
    Phân tích phản hồi khách hàng để đưa ra cảnh báo sức khỏe sản phẩm.
    """
    products = Product.objects.annotate(
        total_reviews=Count('reviews'),
        pos_count=Count('reviews', filter=Q(reviews__sentiment='positive')),
        neu_count=Count('reviews', filter=Q(reviews__sentiment='neutral')),
        neg_count=Count('reviews', filter=Q(reviews__sentiment='negative')),
        avg_rating=Avg('reviews__rating')
    ).prefetch_related('reviews__user')

    data_summary = []
    
    for p in products:
        if p.total_reviews == 0:
            pos_pct = neu_pct = neg_pct = 0
            health, label, tags = 'stable', "Chưa có dữ liệu", ['Mới']
            suggest = "Sản phẩm chưa nhận được đánh giá nào từ người mua."
        else:
            total = p.total_reviews
            pos_pct = (p.pos_count / total) * 100
            neu_pct = (p.neu_count / total) * 100
            neg_pct = (p.neg_count / total) * 100
            
            # Logic phân loại sức khỏe sản phẩm
            if neg_pct > 35:
                health, label, tags = 'critical', "Nguy cơ: Tỷ lệ tiêu cực cao", ['Cần kiểm tra', 'Chất lượng']
                suggest = f"Gửi lời xin lỗi đến khách hàng về sản phẩm {p.name}."
            elif pos_pct > 65:
                health, label, tags = 'healthy', "Tuyệt vời: Khách hàng hài lòng", ['Xu hướng', 'Bán chạy']
                suggest = "Hãy đẩy mạnh quảng bá sản phẩm này trên trang chủ."
            else:
                health, label, tags = 'stable', "Ổn định: Đang phát triển", ['Trung bình']
                suggest = "Thu thập thêm phản hồi để cải thiện dịch vụ."

        data_summary.append({
            'product': p,
            'pos_percent': round(pos_pct, 1),
            'neu_percent': round(neu_pct, 1),
            'neg_percent': round(neg_pct, 1),
            'health_status': health,
            'status_label': label,
            'voice_cloud': tags,
            'trend_value': round((pos_pct - neg_pct) / 10, 1) if p.total_reviews > 0 else 0,
            'recent_reviews': p.reviews.all().order_by('-created_at')[:5],
            'reply_suggestion': suggest,
        })

    return render(request, 'adminpanel/sentiment_analytics.html', {
        'data': data_summary,
        'now': timezone.now(),
        'page_title': "Phân tích cảm xúc khách hàng"
    })