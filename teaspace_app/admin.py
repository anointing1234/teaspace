from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Category, Plane, Cart, CartItem, Order, Address, BankPayment
)
from unfold.admin import ModelAdmin as UnfoldAdmin  # Correct import
from unfold.contrib.inlines.admin import TabularInline  # Use Unfold's inline
from django.utils.html import format_html

# --------------------------
# Custom User Admin
# --------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, UnfoldAdmin):  # Inherit from both
    model = CustomUser
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'full_name', 'phone', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


# --------------------------
# Category Admin
# --------------------------
@admin.register(Category)
class CategoryAdmin(UnfoldAdmin):  # Changed from admin.ModelAdmin
    list_display = ('id', 'name')
    search_fields = ('name',)


# --------------------------
# Plane Admin
# --------------------------

@admin.register(Plane)
class PlaneAdmin(UnfoldAdmin):
    list_display = ('id', 'name', 'type', 'price', 'rating', 'category', 'image_preview', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'type', 'details')

    # Add a small preview of the plane image
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

# --------------------------
# Cart & CartItem Admin
# --------------------------
class CartItemInline(TabularInline):  # Use Unfold's TabularInline
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Cart)
class CartAdmin(UnfoldAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'is_paid', 'total_price')
    inlines = [CartItemInline]
    list_filter = ('is_paid', 'created_at', 'updated_at')
    search_fields = ('user__email',)


# --------------------------
# Order Admin
# --------------------------
@admin.register(Order)
class OrderAdmin(UnfoldAdmin):
    list_display = ('id', 'user', 'cart', 'total_price', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('total_price',)


# --------------------------
# Address Admin
# --------------------------
@admin.register(Address)
class AddressAdmin(UnfoldAdmin):
    list_display = ('id', 'order', 'first_name', 'last_name', 'city', 'state', 'zip_code')
    list_filter = ('city', 'state')
    search_fields = ('first_name', 'last_name', 'city', 'state', 'zip_code', 'email')







@admin.register(BankPayment)
class BankPaymentAdmin(UnfoldAdmin):
    list_display = (
        "name",
        "bank_name",
        "account_name",
        "account_number",
        "routing_number",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "bank_name", "created_at")
    search_fields = ("bank_name", "account_name", "account_number")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("name", "bank_name", "account_name", "account_number", "routing_number", "instructions", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )