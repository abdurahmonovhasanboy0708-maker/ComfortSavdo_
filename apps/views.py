from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Avg, Min, Count, OuterRef, Subquery
from django.shortcuts import render, redirect, get_object_or_404

from .models import Category, Product, Market, Order, OrderItem, Review, Offer


def _nav_context(current_category_slug=None):
    """Har bir sahifada navbar uchun kerak bo'ladigan umumiy ma'lumot."""
    return {
        'nav_categories': Category.objects.filter(is_active=True),
        'current_category_slug': current_category_slug,
    }


def _with_cheapest_market(queryset):
    """Har bir mahsulotga eng arzon narx (min_price) va shu narxdagi market nomini qo'shadi."""
    cheapest_offer = Offer.objects.filter(product=OuterRef('pk'), in_stock=True).order_by('price')
    return queryset.annotate(
        min_price=Min('offers__price'),
        cheapest_market_name=Subquery(cheapest_offer.values('market__name')[:1]),
    )


def home(request):
    context = {
        'categories': Category.objects.filter(is_active=True),
        'products': _with_cheapest_market(Product.objects.filter(is_active=True))
                        .order_by('-created_at')[:8],
    }
    context.update(_nav_context())
    return render(request, 'home.html', context)


def _sorted_products(products, sort):
    """sort='r' -> reyting bo'yicha, aks holda (default 'p') -> avval arzonlari."""
    products = products.annotate(avg_rating=Avg('reviews__rating'))
    if sort == 'r':
        return products.order_by('-avg_rating')
    return products.order_by('min_price')


def catalog(request):
    products = _with_cheapest_market(Product.objects.filter(is_active=True))
    products = _sorted_products(products, request.GET.get('sort'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {'products': page_obj}
    context.update(_nav_context())
    return render(request, 'category.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = _with_cheapest_market(Product.objects.filter(category=category, is_active=True))
    products = _sorted_products(products, request.GET.get('sort'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {'category': category, 'products': page_obj}
    context.update(_nav_context(current_category_slug=slug))
    return render(request, 'category.html', context)


def search(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True, title__icontains=q) \
        .annotate(min_price=Min('offers__price'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {'products': page_obj, 'category': None}
    context.update(_nav_context())
    return render(request, 'category.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.annotate(
            min_price=Min('offers__price'),
            avg_rating=Avg('reviews__rating'),
        ),
        slug=slug, is_active=True,
    )
    context = {'product': product}
    context.update(_nav_context(current_category_slug=product.category.slug))
    return render(request, 'product_detail.html', context)


def product_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={
                'rating': request.POST.get('rating'),
                'comment': request.POST.get('comment'),
            },
        )
        messages.success(request, "Izohingiz uchun rahmat!")
    return redirect('product_detail', slug=slug)


def order_create(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        cheapest_offer = product.offers.order_by('price').first()
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=request.POST.get('customer_name', ''),
            customer_phone=request.POST.get('customer_phone', ''),
            address=request.POST.get('address', ''),
            total_price=cheapest_offer.price if cheapest_offer else 0,
            status='new',
        )
        if cheapest_offer:
            OrderItem.objects.create(order=order, offer=cheapest_offer, price=cheapest_offer.price, quantity=1)
        return redirect('order_success', order_id=order.id)
    return redirect('product_detail', slug=slug)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    context.update(_nav_context())
    return render(request, 'order_success.html', context)


def market_list(request):
    markets = Market.objects.filter(is_active=True)
    context = {'markets': markets}
    context.update(_nav_context())
    return render(request, 'market_list.html', context)


def market_detail(request, slug):
    market = get_object_or_404(Market, slug=slug, is_active=True)
    context = {'market': market}
    context.update(_nav_context())
    return render(request, 'market_detail.html', context)


def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = authenticate(request, username=phone, password=password)
        if user:
            login(request, user)
            return redirect(request.POST.get('next') or 'home')
        messages.error(request, "Telefon yoki parol noto'g'ri")
    context = {}
    context.update(_nav_context())
    return render(request, 'login.html', context)


def register_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone_number')

        if password != confirm_password:
            messages.error(request, "Parollar bir xil emas")
        elif get_user_model_exists(phone):
            messages.error(request, "Bu telefon raqam allaqachon ro'yxatdan o'tgan")
        else:
            # TODO: User.objects.create_user(phone=phone, ...) — sizning User modelingizga moslang
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz, endi kiring")
            return redirect('login')

    context = {}
    context.update(_nav_context())
    return render(request, 'register.html', context)


def get_user_model_exists(phone):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.filter(phone=phone).exists()


def logout_view(request):
    logout(request)
    return redirect('home')


def cabinet(request):
    context = {'orders': Order.objects.filter(user=request.user)[:10]} if request.user.is_authenticated else {}
    context.update(_nav_context())
    return render(request, 'cabinet.html', context)