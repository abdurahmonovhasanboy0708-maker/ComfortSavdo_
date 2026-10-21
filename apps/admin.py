from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import (
    User, Category, Product, ProductImage, Market, Offer,
    Review, Order, OrderItem,
)


# =========================================================
#  USER
# =========================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['phone']
    list_display = ['phone', 'first_name', 'balance', 'is_staff', 'is_active']
    search_fields = ['phone', 'first_name']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Shaxsiy', {'fields': ('first_name', 'last_name', 'ref_code', 'balance')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('phone', 'password1', 'password2')}),
    )


# =========================================================
#  CATEGORY
# =========================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'title', 'slug', 'order', 'is_active']
    list_display_links = ['title']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']

    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('title', 'slug'),
        }),
        ('Ko\'rinishi (bosh sahifadagi karta)', {
            'fields': ('image', 'color', 'subtitle'),
            'description': (
                "<b>Ikonka</b> — oddiy emoji yozing (masalan 📱). "
                "<b>Fon rangi</b> — hex kod (masalan #dbeafe). "
                "<b>Qisqa tavsif</b> — kartada kichik matn sifatida chiqadi."
            ),
        }),
        ('Qo\'shimcha', {
            'fields': ('order', 'is_active'),
            'description': "Tartib raqami kichik bo'lgan kategoriya birinchi chiqadi.",
        }),
    )

    @admin.display(description="Ikonka")
    def icon_preview(self, obj):
        return format_html(
            '<span style="font-size:22px;background:{};padding:4px 8px;border-radius:8px">{}</span>',
            obj.color or '#eee', obj.image or '—',
        )


# =========================================================
#  PRODUCT
# =========================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 4
    fields = ['image', 'is_main', 'order']
    verbose_name = "Mahsulot rasmi"
    verbose_name_plural = "Mahsulot rasmlari (jami 4 tagacha, bittasi 'Is main' — asosiy rasm)"


class OfferInline(admin.TabularInline):
    model = Offer
    extra = 1
    fields = ['market', 'price', 'in_stock']
    verbose_name = "Narx"
    verbose_name_plural = "Narxlar — har bir market uchun alohida narx kiriting"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumb_preview', 'title', 'category', 'min_price_display', 'is_active', 'created_at']
    list_display_links = ['title']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline, OfferInline]

    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('title', 'slug', 'category', 'is_active'),
        }),
        ('Tavsif (description)', {
            'fields': ('description',),
            'description': "Mahsulot sahifasida narx ostida to'liq matn sifatida chiqadi.",
        }),
    )

    @admin.display(description="Rasm")
    def thumb_preview(self, obj):
        img = obj.images.filter(is_main=True).first() or obj.images.first()
        if img:
            return format_html('<img src="{}" style="height:40px;border-radius:6px">', img.image.url)
        return "—"

    @admin.display(description="Eng arzon narx")
    def min_price_display(self, obj):
        cheapest = obj.offers.order_by('price').first()
        if cheapest:
            return f"{cheapest.price:,} so'm".replace(',', ' ')
        return "Narx yo'q"


# =========================================================
#  MARKET
# =========================================================
@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'address']

    fieldsets = (
        ('Asosiy ma\'lumot', {'fields': ('name', 'slug', 'phone', 'work_hours', 'is_active')}),
        ('Manzil va xarita', {
            'fields': ('address', 'latitude', 'longitude'),
            'description': "Latitude/Longitude — Google Maps'dan joylashuvni sichqoncha bilan bosib topib olishingiz mumkin.",
        }),
    )


# =========================================================
#  OFFER (alohida ro'yxat ham kerak bo'lsa)
# =========================================================
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'market', 'price', 'in_stock', 'updated_at']
    list_editable = ['price', 'in_stock']
    list_filter = ['market', 'in_stock']
    search_fields = ['product__title', 'market__name']


# =========================================================
#  REVIEW
# =========================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_visible', 'created_at']
    list_editable = ['is_visible']
    list_filter = ['rating', 'is_visible']
    search_fields = ['product__title', 'user__first_name', 'comment']


# =========================================================
#  ORDER
# =========================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_phone', 'total_price', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['customer_name', 'customer_phone']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Mijoz', {'fields': ('customer_name', 'customer_phone', 'region', 'address')}),
        ('Buyurtma', {'fields': ('user', 'total_price', 'status', 'comment')}),
    )

