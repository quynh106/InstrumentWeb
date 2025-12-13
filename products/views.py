from django.shortcuts import render, get_object_or_404
from .models import Product,Category, Brand, Review
from django.db.models import Avg
from django.shortcuts import redirect


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

# review
    reviews = product.reviews.all()

    star = request.GET.get("star")
    if star and star != "all":
        reviews = reviews.filter(rating=star)

    average_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    total_reviews = reviews.count()

    context = {
        'product': product,
        'related_products': related_products,
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        "reviews": reviews,
        "average_rating": round(average_rating, 1),
        "total_reviews": total_reviews,
    }
    return render(request, 'products/product_detail.html', context)

def review_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        Review.objects.create(
        product=product,
        user=request.user,
        rating=int(request.POST.get("rating", 5)),
        comment=request.POST.get("comment"),
        image=request.FILES.get("image")
    )
        return redirect('products:product_detail', product_id)

    return render(request, 'products/review.html', {
        'product': product
    })
