from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Brand, Review, ReviewImage, FlashSale
from django.db.models import Avg, Count,Case, When
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .sentiment import analyze_sentiment


def home(request):
    # 5 sản phẩm mới nhất cho hero slider
    new_products = Product.objects.all().order_by('-created_at')[:5]
    
    # 8 sản phẩm trending
    trending_products = Product.objects.all()[:8]
    
    #flash sale
    now = timezone.now()

    flash_sales = FlashSale.objects.select_related("product").filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    )

    flash_sale_end = None
    if flash_sales.exists():
        flash_sale_end = flash_sales.order_by("end_time").first().end_time

    # 5 sản phẩm chỗ special, Home Product List
    random_products = (
    Product.objects
    .annotate(avg_rating=Avg("reviews__rating"))
    .order_by('?')
)
    

    # Tính avg_rating
    for product in trending_products:
        product.avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    #filter cat && brand & search
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    # Clean up empty values
    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    # Get filtered products
    products = (
        Product.get_filtered_products(search_query, category_id, brand_id)
        .annotate(avg_rating=Avg("reviews__rating"))
    )
    
    CATEGORY_ORDER = [
    "Guitar",
    "Piano",
    "Drums",
    "Flute",
    "Violin",
   
]

    feature_categories = Category.objects.filter(
    name__in=CATEGORY_ORDER
).annotate(
    custom_order=Case(
        *[When(name=name, then=pos) for pos, name in enumerate(CATEGORY_ORDER)]
    )
).order_by("custom_order")
    
    context = {
        'new_products': new_products,
        "flash_sales": flash_sales,
        "flash_sale_end": flash_sale_end,
        'trending_products': trending_products,
        'random_products': random_products,
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all().all(),
        'feature_categories' : feature_categories,

    }
    
    return render(request, 'products/home.html', context)


def product_list(request):
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    sort_by = request.GET.get('sort', '')
    max_price = request.GET.get('max_price', '')

    # Clean up empty values
    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    # Get filtered products
    products = (
        Product.get_filtered_products(search_query, category_id, brand_id)
        .annotate(avg_rating=Avg("reviews__rating"))
    )

    # Apply price filter
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Apply sorting
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created_at")

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
    #filter cat && brand & search
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    # Clean up empty values
    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    # Get filtered products
    products = (
        Product.get_filtered_products(search_query, category_id, brand_id)
        .annotate(avg_rating=Avg("reviews__rating"))
    )

    #
    product = get_object_or_404(Product, pk=pk)
    product_images = product.images.all()

    # Related products - 4 sản phẩm
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]
    
    # Tính avg_rating cho related products
    for p in related_products:
        p.avg_rating = p.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # ===== REVIEWS =====
    all_reviews = Review.objects.filter(
        product=product
    ).select_related("user")

    

    # Filter theo sao
    star = request.GET.get("star", "all")
    reviews = Review.objects.filter(product=product)
    
    if star and star != "all":
        try:
            star_int = int(star)
            reviews = reviews.filter(rating=star_int)
        except ValueError:
            pass

    # Average & total
    average_rating = all_reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    total_reviews = all_reviews.count()

    # Đếm số review mỗi sao
    rating_counts = (
        all_reviews.values("rating")
        .annotate(count=Count("id"))
    )
    counts_map = {item["rating"]: item["count"] for item in rating_counts}

    star_filters = []
    for i in range(5, 0, -1):
        star_filters.append({
            "star": i,
            "count": counts_map.get(i, 0)
        })

    # ===== AJAX REQUEST =====
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for r in reviews:
            data.append({
                "user": r.user.username,
                "rating": r.rating,
                "comment": r.comment,
                "date": r.created_at.strftime("%b %d, %Y"),
                "images": [img.image.url for img in r.images.all()],
            })
        return JsonResponse({"reviews": data})

    # ===== NORMAL REQUEST =====
    return render(request, "products/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "average_rating": round(average_rating, 1),
        "total_reviews": total_reviews,
        "star_filters": star_filters,
        "product_images": product_images,
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all().all(),
    })





@login_required
def review_product(request, product_id):
    #filter cat && brand & search
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    # Clean up empty values
    if category_id in ('', 'None'):
        category_id = None
    if brand_id in ('', 'None'):
        brand_id = None

    # Get filtered products
    products = (
        Product.get_filtered_products(search_query, category_id, brand_id)
        .annotate(avg_rating=Avg("reviews__rating"))
    )

    #
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        comment = request.POST.get("comment", "").strip()
        rating = int(request.POST.get("rating", 5))
        rating = max(1, min(rating, 5))

        sentiment = analyze_sentiment(comment)

        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
            sentiment=sentiment
        )

        # Save images
        for img in request.FILES.getlist("images"):
            ReviewImage.objects.create(
                review=review,
                image=img
            )

        return redirect('products:product_detail', pk=product_id)  # FIX: pk thay vì product_id

    return render(request, 'products/review.html', {
        'product': product,
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all().all(),
    })