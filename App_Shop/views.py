from django.shortcuts import render
from django.shortcuts import get_object_or_404 , redirect
from django.shortcuts import render, get_object_or_404
from django.db.models import Q , Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail

from .models import Product, Category, AgeGroup, ClothingType, Review
from App_Order.models import OrderItem


def home(request):
    products = Product.objects.select_related('category', 'age_group', 'clothing_type').all()

    new_arrivals = products.order_by('-pk')[:8]
    best_sellers = products.order_by('?')[:8]  # Random for now, could be ordered by sales

    # If user is not logged in → show all products normally
    if not request.user.is_authenticated:
        return render(request, 'App_Shop/home.html', {
            'products': products[:8],
            'new_arrivals': new_arrivals,
            'best_sellers': best_sellers,
        })

    # 🧠 Step 1: Get user preferences

    purchased_categories = Category.objects.filter(
        product__orderitem__order__user=request.user,
        product__orderitem__order__ordered=True
    ).distinct()

    purchased_age_groups = AgeGroup.objects.filter(
        product__orderitem__order__user=request.user,
        product__orderitem__order__ordered=True
    ).distinct()

    purchased_clothing_types = ClothingType.objects.filter(
        product__orderitem__order__user=request.user,
        product__orderitem__order__ordered=True
    ).distinct()

    # 🧠 Step 2: Get preferred products (match ANY preference)

    preferred_products = Product.objects.select_related('category', 'age_group', 'clothing_type').filter(
        Q(category__in=purchased_categories) |
        Q(age_group__in=purchased_age_groups) |
        Q(clothing_type__in=purchased_clothing_types)
    ).distinct()

    # 🧠 Step 3: Get remaining products

    remaining_products = Product.objects.select_related('category', 'age_group', 'clothing_type').exclude(
        id__in=preferred_products.values_list('id', flat=True)
    )

    # 🧠 Step 4: Combine (preferred first)

    final_products = list(preferred_products) + list(remaining_products)

    return render(request, 'App_Shop/home.html', {
        'products': final_products[:8],
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
    })


def search_products(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('cat', '').strip()

    matched = Product.objects.none()
    remaining = Product.objects.none()

    if category_id:
        # Category filter — show category products first, then all others
        matched = Product.objects.select_related('category', 'age_group', 'clothing_type').filter(
            category__id=category_id
        )
        remaining = Product.objects.select_related('category', 'age_group', 'clothing_type').exclude(
            category__id=category_id
        )
    elif query:
        matched = Product.objects.select_related('category', 'age_group', 'clothing_type').filter(
            Q(name__icontains=query) |
            Q(detail_text__icontains=query) |
            Q(category__name__icontains=query) |
            Q(clothing_type__name__icontains=query)
        ).distinct()
        remaining = Product.objects.select_related('category', 'age_group', 'clothing_type').exclude(
            id__in=matched.values_list('id', flat=True)
        )

    # For empty search — show popular/random products
    interested = Product.objects.order_by('?')[:8] if not query and not category_id else None

    return render(request, 'App_Shop/search_results.html', {
        'query': query,
        'category_id': category_id,
        'products': matched,
        'remaining': remaining,
        'interested': interested,
    })



@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # 🔐 Step 1: Check if user actually purchased product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__ordered=True
    ).exists()

    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect('App_Shop:product_detail', pk=pk)

    # ⭐ Step 2: Handle POST
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Optional: prevent multiple reviews per user per product
        existing_review = Review.objects.filter(
            user=request.user,
            product=product
        ).first()

        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review added successfully.")

        return redirect('App_Shop:product_detail', pk=pk)

    return redirect('App_Shop:product_detail', pk=pk)


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'age_group', 'clothing_type'), pk=pk)

    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # check if user can review
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__ordered=True
        ).exists()

    return render(request, 'App_Shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_review': can_review,
        'related_products': Product.objects.filter(category=product.category).exclude(pk=product.pk)[:8],
    })



def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'App_Shop/category.html', {
        'category': category,
        'products': products,
    })


def products_by_category_slug(request, slug):
    """Lookup a category by case-insensitive name match (slug = lowercase name)."""
    category = get_object_or_404(Category, name__iexact=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'App_Shop/category.html', {
        'category': category,
        'products': products,
    })


def products_by_age(request, age_id):
    age_group = get_object_or_404(AgeGroup, id=age_id)
    products = Product.objects.filter(age_group=age_group)
    return render(request, 'App_Shop/category.html', {
        'category': age_group,
        'products': products,
    })


def products_by_clothing(request, type_id):
    clothing_type = get_object_or_404(ClothingType, id=type_id)
    products = Product.objects.filter(clothing_type=clothing_type)
    return render(request, 'App_Shop/category.html', {
        'category': clothing_type,
        'products': products,
    })


def about_us(request):
    return render(request, 'App_Shop/about.html')


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_body = request.POST.get('message', '').strip()

        if name and email and message_body:
            try:
                send_mail(
                    subject=f'AURA Contact Form — {name}',
                    message=f'From: {name} <{email}>\n\n{message_body}',
                    from_email=email,
                    recipient_list=['basiljosephgjms123456@gmail.com'],
                    fail_silently=True,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception:
                messages.success(request, 'Your message has been received!')
        else:
            messages.warning(request, 'Please fill in all required fields.')

        return redirect('App_Shop:contact')

    return render(request, 'App_Shop/contact.html')

