from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# =========================================================
#  USER
# =========================================================
class UserManager(models.Manager):
    def get_by_natural_key(self, phone):
        return self.get(phone=phone)

    def create_user(self, phone, password=None, **extra):
        if not phone:
            raise ValueError("Telefon raqam kiritilishi shart")
        user = self.model(phone=phone, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra)


class User(AbstractUser):
    username = None
    phone = models.CharField(max_length=20, unique=True)
    ref_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    balance = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.first_name or self.phone


# =========================================================
#  CATEGORY
# =========================================================
class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.TextField(
        blank=True,
        verbose_name="Ikonka (emoji)",
        help_text="Bu yerga oddiy emoji yozing, masalan: 📱 yoki 👕 yoki 🏠. Rasm fayl emas — matn sifatida yoziladi."
    )
    subtitle = models.CharField(max_length=200, blank=True)
    color = models.CharField(
        max_length=7, blank=True, default='#dbeafe',
        help_text="Tile foni, masalan #dbeafe (home.html dagi kartalar uchun)"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.title


# =========================================================
#  PRODUCT
# =========================================================
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.title

    @property
    def thumbnail_image(self):
        """home.html / category.html da {{ product.thumbnail_image.image.url }} shaklida ishlatiladi."""
        return self.images.filter(is_main=True).first() or self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"

    def __str__(self):
        return f"{self.product.title} — rasm"


# =========================================================
#  MARKET
# =========================================================
class Market(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=20, blank=True)
    work_hours = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Marketlar"

    def __str__(self):
        return self.name


# =========================================================
#  OFFER  (mahsulotning shu marketdagi narxi)
# =========================================================
class Offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='offers')
    price = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'market')
        ordering = ['price']
        verbose_name = "Narx (Offer)"
        verbose_name_plural = "Narxlar (Offer)"

    def __str__(self):
        return f"{self.product.title} — {self.market.name}: {self.price} so'm"


# =========================================================
#  REVIEW
# =========================================================
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"

    def __str__(self):
        return f"{self.user} → {self.product} ({self.rating}★)"


# =========================================================
#  ORDER
# =========================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('processing', 'Jarayonda'),
        ('confirmed', 'Tasdiqlangan'),
        ('shipped', "Yo'lda"),
        ('delivered', 'Yetkazildi'),
        ('no_answer', 'Javob bermadi'),
        ('cancelled', 'Bekor qilindi'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    region = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"Buyurtma #{self.id} — {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name='order_items')
    price = models.PositiveIntegerField(help_text="Buyurtma paytidagi narx")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Buyurtma tarkibi"
        verbose_name_plural = "Buyurtma tarkiblari"

    def __str__(self):
        return f"{self.offer.product.title} x{self.quantity}"

    @property
    def total(self):
        return self.price * self.quantity