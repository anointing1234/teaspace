from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, full_name, password=None, phone=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, full_name, password=None, phone=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, full_name, password, phone, **extra_fields)


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # email will be used to log in
    REQUIRED_FIELDS = ['username', 'full_name']  # required when creating superuser

    def __str__(self):
        return self.email




# --------------------------
# Product Categories
# --------------------------
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# --------------------------
# Products (Planes)
# --------------------------
class Plane(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='planes')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    details = models.TextField()
    image = models.ImageField(upload_to='planes/', blank=True, null=True)  # NEW field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# --------------------------
# Cart & Cart Items
# --------------------------
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} - {self.user.email}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.plane.name}"

    @property
    def total_price(self):
        return self.plane.price * self.quantity


# --------------------------
# Orders & Addresses
# --------------------------
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.user.email}"


class Address(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    # Billing Details
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Optional Shipping Details
    ship_to_different = models.BooleanField(default=False)
    ship_first_name = models.CharField(max_length=255, blank=True, null=True)
    ship_last_name = models.CharField(max_length=255, blank=True, null=True)
    ship_company = models.CharField(max_length=255, blank=True, null=True)
    ship_address = models.CharField(max_length=255, blank=True, null=True)
    ship_apartment = models.CharField(max_length=255, blank=True, null=True)
    ship_city = models.CharField(max_length=255, blank=True, null=True)
    ship_state = models.CharField(max_length=255, blank=True, null=True)
    ship_zip_code = models.CharField(max_length=20, blank=True, null=True)
    ship_email = models.EmailField(blank=True, null=True)
    ship_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Address for Order {self.order.id}"
    




class BankPayment(models.Model):
    name = models.CharField(max_length=100, default="Bank Transfer", help_text="Payment method name")
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True, help_text="Optional instructions to display at checkout")
    is_active = models.BooleanField(default=True, help_text="Display this payment method on checkout")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bank Payment"
        verbose_name_plural = "Bank Payments"

    def __str__(self):
        return self.name
    



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    plane = models.ForeignKey(Plane, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.plane.name}"

    @property
    def total_price(self):
        return self.price * self.quantity
