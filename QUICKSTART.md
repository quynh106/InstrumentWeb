# Quick Start Guide

## Chạy server ngay lập tức

### Bước 1: Activate virtual environment
```bash
cd InstrumentWeb-main
venv\Scripts\activate
```

### Bước 2: Chạy server
```bash
python manage.py runserver
```

## Truy cập ứng dụng

### 🌐 Website chính
**http://127.0.0.1:8000/**

### 👨‍💼 Admin Panel (Phần bạn làm)
**http://127.0.0.1:8000/adminpanel/**

Features:
- Dashboard với thống kê
- Quản lý đơn hàng (Order Management)
- Quản lý kho (Inventory)
- Thống kê (Statistics)

### ⚙️ Django Admin (CRUD)
**http://127.0.0.1:8000/admin/**

## Tạo Admin User (Cần làm một lần)

```bash
python manage.py createsuperuser
```

Thông tin mẫu:
- Username: `admin`
- Email: `admin@test.com`
- Password: `admin123`

## Tạo dữ liệu mẫu

Sau khi tạo superuser, truy cập Django Admin và tạo:

1. **Categories**: Guitar, Piano, Drums
2. **Brands**: Yamaha, Fender, Gibson
3. **Products**: Thêm 5-10 sản phẩm với giá, stock
4. **Orders**: Tạo một vài đơn hàng để test

## URLs quan trọng

| Tính năng | URL | Mô tả |
|-----------|-----|-------|
| Trang chủ | `/` | Danh sách sản phẩm |
| Admin Dashboard | `/adminpanel/` | Dashboard thống kê |
| Quản lý đơn hàng | `/adminpanel/orders/` | Danh sách & chi tiết đơn hàng |
| Quản lý kho | `/adminpanel/inventory/` | Cập nhật stock |
| Thống kê | `/adminpanel/statistics/` | Reports |
| Django Admin | `/admin/` | CRUD interface |

## Tính năng Admin Panel

### 📊 Dashboard
- Tổng đơn hàng, doanh thu
- Đơn hàng pending
- Sản phẩm low stock
- Top 5 sản phẩm bán chạy

### 📦 Order Management
- Danh sách đơn hàng với filter
- Cập nhật trạng thái: Pending → Paid → Shipped → Completed
- Chi tiết đơn hàng

### 📦 Inventory Management
- Danh sách sản phẩm với stock
- Cập nhật stock (Add/Remove/Adjust)
- Low stock warning

### 📈 Statistics
- Thống kê theo category
- Thống kê theo brand
- Thống kê theo order status

## Lưu ý

⚠️ **Quan trọng**: Phải tạo superuser và login trước khi truy cập `/adminpanel/`

✅ Server đã chạy thành công tại: **http://127.0.0.1:8000/**

✅ Database đã migrate xong

✅ Tất cả templates đã được tạo

## Cấu trúc code bạn làm

```
adminpanel/
├── models.py           # InventoryLog model
├── views.py            # Dashboard, Orders, Inventory, Statistics views
├── urls.py             # URL routing
├── admin.py            # Django admin config
└── templates/
    └── adminpanel/
        ├── base_admin.html      # Base template với sidebar
        ├── dashboard.html       # Dashboard chính
        ├── order_list.html      # Danh sách đơn hàng
        ├── order_detail.html    # Chi tiết đơn hàng
        ├── inventory_list.html  # Danh sách kho
        ├── inventory_update.html # Cập nhật stock
        └── statistics.html      # Thống kê
```

## Tips

1. **Test Order Management**: Tạo orders với status khác nhau để test filter
2. **Test Inventory**: Thay đổi stock để thấy màu warning (đỏ < 10, vàng < 20)
3. **Test Statistics**: Tạo nhiều products trong các categories khác nhau
4. **View Code**: Tất cả views có comments rõ ràng bằng tiếng Việt

---

**🎉 Chúc bạn demo thành công!**
