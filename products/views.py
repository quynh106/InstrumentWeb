from django.shortcuts import render, get_object_or_404
from .models import Product,Category, Brand


def product_list(request):
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')


    # filter
    sort_by = request.GET.get('sort')

    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    products = Product.get_filtered_products(search_query, category_id, brand_id)

   


    # APPLY SORTING
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
   

    context = {
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    
    product = get_object_or_404(Product, pk=pk)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:6]

    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')


    # filter
    sort_by = request.GET.get('sort')

    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    products = Product.get_filtered_products(search_query, category_id, brand_id)

    context = {
        'product': product,
        'related_products': related_products,
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'products/product_detail.html', context)

