# products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand # Cần import cả 3 models này

def product_list(request):
    # Lấy tham số tìm kiếm từ URL
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')

    # Xử lý giá trị None (để truyền vào get_filtered_products)
    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    # Gọi phương thức tĩnh từ Class Product
    products = Product.get_filtered_products(search_query, category_id, brand_id)
    
    # Chuẩn bị Context để truyền vào template
    context = {
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(), # Truyền danh sách Category để hiển thị Filter
        'brands': Brand.objects.all(),       # Truyền danh sách Brand để hiển thị Filter
    }
    
    # Hiển thị template
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug): # Đã thay product_id bằng slug
    """Hiển thị chi tiết một sản phẩm."""
    # Tìm sản phẩm bằng slug thay vì id
    product = get_object_or_404(Product, slug=slug) 
    context = {'product': product}
    return render(request, 'products/product_detail.html', context)
def home(request):
    # Lấy danh sách sản phẩm (chưa lọc)
    products = Product.objects.filter(is_available=True).order_by('-created_at')[:8] # Lấy 8 sản phẩm mới nhất
    
    # Lấy Category và Brand để hiển thị trên Header/Navbar
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        # Thêm các biến khác cho Header nếu cần (brand_id, search_query, category_id)
        'brand_id': request.GET.get('brand'),
        'search_query': request.GET.get('q'),
        'category_id': request.GET.get('category'),
    }
    return render(request, 'products/index.html', context)