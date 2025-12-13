from django.shortcuts import render, get_object_or_404, redirect
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Product
from django.contrib.auth.decorators import login_required

# Xem giỏ hàng (GET)
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    return render(request, 'cart.html', {'cart': cart, 'items': items})

# Thêm sản phẩm vào giỏ (POST)
@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        cart, created = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity += 1
        item.save()
    return redirect('view_cart')

# Xóa sản phẩm khỏi giỏ (POST)
@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
    return redirect('view_cart')

# Checkout - tạo đơn hàng (POST)
@login_required
def create_order(request):
    if request.method == "POST":
        cart = get_object_or_404(Cart, user=request.user)
        total = sum(i.product.price * i.quantity for i in cart.items.all())
        order = Order.objects.create(user=request.user, total_price=total)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_time=item.product.price
            )
        cart.items.all().delete()  # xóa giỏ hàng sau khi đặt
    return redirect('order_history')

# Xem lịch sử đơn hàng (GET)
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})

