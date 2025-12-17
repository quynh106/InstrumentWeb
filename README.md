# InstrumentWeb - Website Bán Nhạc Cụ

Django web application cho việc bán nhạc cụ trực tuyến với Admin Panel đầy đủ.

## Cấu trúc Project

```
InstrumentWeb-main/
├── InstrumentWeb/          # Main project settings
│   ├── settings.py         # Cấu hình Django
│   ├── urls.py            # URL routing chính
│   └── wsgi.py
├── products/              # App quản lý sản phẩm
│   ├── models.py          # Category, Brand, Product, Review
│   ├── views.py           # Product list, detail
│   └── templates/
├── users/                 # App quản lý người dùng
│   ├── models.py          # UserProfile
│   └── views.py           # Cart, Order views
├── cart/                  # App giỏ hàng
│   └── models.py          # Cart, CartItem
├── orders/                # App đơn hàng
│   ├── models.py          # Order, OrderItem
│   └── admin.py           # Order admin interface
├── adminpanel/            # App quản trị (PHẦN BẠN PHỤ TRÁCH)
│   ├── models.py          # InventoryLog
│   ├── views.py           # Dashboard, Order Management, Inventory, Statistics
│   ├── urls.py            # Admin panel URLs
│   └── templates/         # Admin templates
├── templates/             # Shared templates
│   └── base.html
├── static/                # CSS, JS, Images
├── manage.py
└── requirements.txt
```

## Tính năng đã implement

### 1. Products App (Hoàn thành)
- ✅ Models: Category, Brand, Product, Review
- ✅ Danh sách sản phẩm với tìm kiếm, lọc theo category/brand
- ✅ Chi tiết sản phẩm với reviews
- ✅ Sắp xếp theo giá

### 2. Cart & Orders App (Models hoàn thành)
- ✅ Models Cart, CartItem
- ✅ Models Order, OrderItem
- ✅ Views để xem giỏ hàng, thêm/xóa sản phẩm
- ✅ Checkout và tạo đơn hàng

### 3. Admin Panel (PHẦN BẠN PHỤ TRÁCH - ĐÃ HOÀN THÀNH)
- ✅ **Dashboard**: Thống kê tổng quan
  - Tổng đơn hàng, doanh thu
  - Đơn hàng pending
  - Sản phẩm tồn kho thấp
  - Top 5 sản phẩm bán chạy
  - Đơn hàng gần đây

- ✅ **Order Management**: Quản lý đơn hàng
  - Danh sách đơn hàng với filter theo status
  - Tìm kiếm đơn hàng
  - Chi tiết đơn hàng
  - Cập nhật trạng thái đơn hàng (Pending → Paid → Shipped → Completed)

- ✅ **Inventory Management**: Quản lý kho
  - Danh sách sản phẩm với stock
  - Cảnh báo low stock (màu đỏ/vàng/xanh)
  - Cập nhật stock (Add/Remove/Adjust)
  - Ghi log inventory changes

- ✅ **Statistics**: Thống kê
  - Thống kê theo category
  - Thống kê theo brand
  - Thống kê đơn hàng theo trạng thái

- ✅ **Django Admin CRUD**:
  - Product, Category, Brand admin
  - Order admin với inline OrderItems
  - InventoryLog admin

## Cài đặt và Chạy Project

### 1. Tạo môi trường ảo

```bash
cd InstrumentWeb-main
python -m venv venv
```

### 2. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Chạy migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Tạo superuser (để truy cập admin)

```bash
python manage.py createsuperuser
```

Nhập thông tin:
- Username: admin
- Email: admin@example.com
- Password: admin123 (hoặc password bạn muốn)

### 6. Tạo dữ liệu mẫu (Optional)

Truy cập Django Admin và tạo data mẫu:
```bash
python manage.py runserver
```

Mở trình duyệt và truy cập: http://127.0.0.1:8000/admin/

Tạo:
- 2-3 Categories (Guitar, Piano, Drums, etc.)
- 2-3 Brands (Yamaha, Fender, Gibson, etc.)
- 5-10 Products với thông tin đầy đủ
- Một vài Orders để test

### 7. Chạy server

```bash
python manage.py runserver
```

## Truy cập ứng dụng

### Website chính (Customer)
- **Trang chủ**: http://127.0.0.1:8000/
- **Danh sách sản phẩm**: http://127.0.0.1:8000/
- **Chi tiết sản phẩm**: http://127.0.0.1:8000/{product_id}/

### Admin Panel (PHẦN BẠN PHỤ TRÁCH)
- **Dashboard**: http://127.0.0.1:8000/adminpanel/
- **Order Management**: http://127.0.0.1:8000/adminpanel/orders/
- **Inventory**: http://127.0.0.1:8000/adminpanel/inventory/
- **Statistics**: http://127.0.0.1:8000/adminpanel/statistics/

### Django Admin (CRUD)
- **Django Admin**: http://127.0.0.1:8000/admin/

## Models

### Products App

**Category**
- name: CharField

**Brand**
- name: CharField

**Product**
- name, description, price, stock
- category: ForeignKey(Category)
- brand: ForeignKey(Brand)
- image: ImageField
- created_at: DateTimeField

**Review**
- product: ForeignKey(Product)
- user: ForeignKey(User)
- rating, comment
- image: ImageField
- created_at: DateTimeField

### Cart App

**Cart**
- user: ForeignKey(User)
- created_at: DateTimeField

**CartItem**
- cart: ForeignKey(Cart)
- product: ForeignKey(Product)
- quantity: PositiveIntegerField

### Orders App

**Order**
- user: ForeignKey(User)
- total_price: DecimalField
- status: CharField (pending, paid, shipped, completed, cancelled)
- created_at, updated_at: DateTimeField

**OrderItem**
- order: ForeignKey(Order)
- product: ForeignKey(Product)
- quantity, price_at_time: IntegerField, DecimalField

### AdminPanel App

**InventoryLog**
- product: ForeignKey(Product)
- action: CharField (add, remove, adjust)
- quantity, previous_stock, new_stock: IntegerField
- notes: TextField
- created_by: ForeignKey(User)
- created_at: DateTimeField

## API Endpoints (AdminPanel)

### Dashboard
- `GET /adminpanel/` - Dashboard với thống kê tổng quan

### Order Management
- `GET /adminpanel/orders/` - Danh sách đơn hàng
- `GET /adminpanel/orders/{id}/` - Chi tiết đơn hàng
- `POST /adminpanel/orders/{id}/update-status/` - Cập nhật trạng thái

### Inventory Management
- `GET /adminpanel/inventory/` - Danh sách sản phẩm và stock
- `GET /adminpanel/inventory/{product_id}/update/` - Form cập nhật stock
- `POST /adminpanel/inventory/{product_id}/update/` - Xử lý cập nhật stock

### Statistics
- `GET /adminpanel/statistics/` - Thống kê chi tiết

## Security

- Tất cả admin views đều được bảo vệ bằng `@login_required` và `@user_passes_test(is_admin)`
- Chỉ staff/superuser mới có thể truy cập admin panel
- CSRF protection được bật mặc định

## Cấu trúc Database

Database: SQLite3 (mặc định của Django)
File: `db.sqlite3`

## Requirements

- Python 3.8+
- Django 5.0.0
- Pillow 10.2.0 (cho ImageField)

## Phần việc đã hoàn thành

1. ✅ Di chuyển models về đúng app (Cart → cart, Order → orders)
2. ✅ Sửa lỗi import trong users/views.py
3. ✅ Tạo InventoryLog model
4. ✅ Cấu hình Django Admin cho tất cả models
5. ✅ Implement đầy đủ AdminPanel views (Dashboard, Orders, Inventory, Statistics)
6. ✅ Tạo URLs routing cho adminpanel
7. ✅ Tạo templates đầy đủ với Bootstrap 5
8. ✅ Implement tính năng tìm kiếm, filter, update status
9. ✅ Inventory logging system

## Ghi chú

- Database đã được migrate và sẵn sàng sử dụng
- Cần tạo superuser để truy cập admin
- Cần tạo data mẫu (Categories, Brands, Products) để test
- Static files đang dùng CDN (Bootstrap 5)
- Images sẽ được lưu trong thư mục `static/products/images/`

## Troubleshooting

### Lỗi "No module named django"
```bash
# Đảm bảo đã activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi database locked
```bash
# Dừng tất cả Django processes và chạy lại
python manage.py runserver
```

### Lỗi static files not found
```bash
# Tạo thư mục static
mkdir static

# Hoặc collect static files
python manage.py collectstatic
```

## Liên hệ

- Người thực hiện: Người 3 - Order Admin + Quản Trị + Kho + Thống Kê
- App phụ trách: adminpanel
