from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product, Category, Brand
from .models import InventoryLog

# Helper function: kiểm tra user có phải admin không
def is_admin(user):
    return user.is_staff or user.is_superuser

# ============== DASHBOARD ==============
@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Thống kê tổng quan
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()

    # Doanh thu 7 ngày gần nhất
    last_7_days = timezone.now() - timedelta(days=7)
    recent_revenue = Order.objects.filter(created_at__gte=last_7_days).aggregate(total=Sum('total_price'))['total'] or 0

    # Đơn hàng gần đây
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

   # Sản phẩm bán chạy nhất
    top_products = Product.objects.annotate(
    total_sold=Sum('orders_app_order_items__quantity') 
    ).order_by('-total_sold')[:5]

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_revenue': recent_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'adminpanel/dashboard.html', context)

# ============== ORDER MANAGEMENT ==============
@login_required
@user_passes_test(is_admin)
def order_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    orders = Order.objects.all()

    if status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        orders = orders.filter(
            Q(id__icontains=search) | Q(user__username__icontains=search)
        )

    orders = orders.order_by('-created_at')

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'adminpanel/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'adminpanel/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def order_update_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    return redirect('adminpanel:order_detail', order_id=order_id)

# ============== INVENTORY MANAGEMENT ==============
@login_required
@user_passes_test(is_admin)
def inventory_list(request):
    search = request.GET.get('q', '')
    products = Product.objects.all()

    if search:
        products = products.filter(Q(name__icontains=search) | Q(brand__name__icontains=search))

    products = products.order_by('stock')

    context = {
        'products': products,
        'search': search,
    }
    return render(request, 'adminpanel/inventory_list.html', context)

@login_required
@user_passes_test(is_admin)
def inventory_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')

        previous_stock = product.stock

        if action == 'add':
            product.stock += quantity
        elif action == 'remove':
            product.stock -= quantity
        elif action == 'adjust':
            product.stock = quantity

        product.save()

        # Ghi log
        InventoryLog.objects.create(
            product=product,
            action=action,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=product.stock,
            notes=notes,
            created_by=request.user
        )

        return redirect('adminpanel:inventory_list')

    context = {'product': product}
    return render(request, 'adminpanel/inventory_update.html', context)

# ============== STATISTICS ==============
@login_required
@user_passes_test(is_admin)
def statistics(request):
    # Thống kê theo category
    category_stats = Category.objects.annotate(
        product_count=Count('products'),
        total_sold=Sum('products__orders_app_order_items__quantity') # Sửa ở đây
    )

    # Thống kê theo brand
    brand_stats = Brand.objects.annotate(
        product_count=Count('products'),
        total_sold=Sum('products__orders_app_order_items__quantity') # Sửa ở đây
    )
    
    # Thống kê đơn hàng theo trạng thái
    order_stats = Order.objects.values('status').annotate(
        count=Count('id'),
        total_revenue=Sum('total_price')
    )

    context = {
        'category_stats': category_stats,
        'brand_stats': brand_stats,
        'order_stats': order_stats,
    }
    return render(request, 'adminpanel/statistics.html', context)
