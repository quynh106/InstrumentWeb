import os
import django
import random
from datetime import datetime, timedelta

# 1. Thiet lap moi truong Django
# Luu y: 'InstrumentWeb' phai trung voi ten thu muc chua file settings.py cua ban
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InstrumentWeb.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from orders.models import Order, OrderItem
from products.models import Product

def run():
    print("--- Dang bat dau qua trinh tao du lieu mau ---")
    
    # Lay tai khoan admin dau tien
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("Loi: Ban can tao Superuser truoc (python manage.py createsuperuser)")
        return

    # Lay danh sach san pham da load tu data.json
    products = list(Product.objects.all())
    if not products:
        print("Loi: Database chua co san pham. Hay chay: python manage.py loaddata data.json")
        return

    # Ngay bat dau: 01/01/2026
    start_date = datetime(2026, 1, 1)
    
    for i in range(24):
        # Tao ngay thang cu the cho moi don hang
        current_date = timezone.make_aware(start_date + timedelta(days=i))
        
        # Tao don hang voi trang thai da hoan thanh
        order = Order.objects.create(
            user=admin_user,
            status='completed',
            total_price=0
        )
        
        # Them ngau nhien 1-3 san pham vao moi don hang
        total_order_price = 0
        items_to_add = random.sample(products, k=random.randint(1, min(3, len(products))))
        
        for p in items_to_add:
            qty = random.randint(1, 2)
            OrderItem.objects.create(
                order=order,
                product=p,
                quantity=qty,
                price_at_time=p.price
            )
            total_order_price += (p.price * qty)
        
        # Cap nhat tong tien va thoi gian tao (de vuot qua auto_now_add)
        Order.objects.filter(id=order.id).update(
            total_price=total_order_price,
            created_at=current_date
        )
        print(f"[*] Da tao don hang cho ngay: {current_date.strftime('%Y-%m-%d')} | Tong: ${total_order_price}")

    print("--- HOAN THANH: 24 ngay du lieu da san sang! ---")

if __name__ == '__main__':
    run()