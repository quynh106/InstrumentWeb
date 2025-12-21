from django.shortcuts import render, get_object_or_404
from .models import Product,Category, Brand, Review
from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.http import JsonResponse

from .sentiment import is_negative_comment
from django.contrib.auth.decorators import login_required


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
   
    # 5 new products
    new_products = Product.objects.order_by('-created_at')[:5]

    context = {
        'products': products,
        'search_query': search_query,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'new_products': new_products,
    }
    return render(request, 'products/product_list.html', context)





def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:6]

    # ===== REVIEWS =====
    all_reviews = Review.objects.filter(
    product=product
).select_related("user") #tối ưu query, tránh N+1

    visible_reviews = all_reviews.filter(is_hidden=False) #chỉ lấy review không bị AI + rule ẩn

    


    # filter theo sao
    star = request.GET.get("star")
    reviews = visible_reviews
    if star and star != "all":
        reviews = reviews.filter(rating=int(star))

    # average & total
    average_rating = all_reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    total_reviews = all_reviews.count()

    # đếm số review mỗi sao
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

    # ===== AJAX FILTER =====
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for r in reviews:
            data.append({
                "user": r.user.username,
                "rating": r.rating,
                "comment": r.comment,
                "date": r.created_at.strftime("%Y-%m-%d"),
                "image": r.image.url if r.image else None,
            })
        return JsonResponse({"reviews": data})

    return render(request, "products/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "average_rating": round(average_rating, 1),
        "total_reviews": total_reviews,
        "star_filters": star_filters,
    })



BAD_WORDS = [      #Rule-based dùng để bắt toxic rõ ràng, nhanh và chính xác.
    "lừa đảo", "rác", "tệ", "chán", "dở",
    "vcl", "đm", "shit", "không đáng tiền"
]


# def review_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == "POST":
#         Review.objects.create(
#         product=product,
#         user=request.user,
#         rating=int(request.POST.get("rating", 5)),
#         comment=request.POST.get("comment"),
#         image=request.FILES.get("image")
#     )
#         return redirect('products:product_detail', product_id)

#     return render(request, 'products/review.html', {
#         'product': product
#     })

@login_required
def review_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        comment = request.POST.get("comment", "").strip()
        rating = int(request.POST.get("rating", 5))
        rating = max(1, min(rating, 5))

        # =====  RULE + AI  để ẩn comment tiêu cực =====
        is_hidden = False

        # Tầng 1: Rule-based
        lower_comment = comment.lower()
        if any(word in lower_comment for word in BAD_WORDS):
            is_hidden = True

        # Tầng 2: AI sentiment
        elif is_negative_comment(comment):
            is_hidden = True

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,      # ⭐ sao giữ nguyên
            comment=comment,
            image=request.FILES.get("image"),
            is_hidden=is_hidden
        )

        return redirect('products:product_detail', product_id)

    return render(request, 'products/review.html', {
        'product': product
    })
