from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password,check_password
from django.views.decorators.csrf import csrf_exempt
from .models import (
    CustomUser,
    Plane, Category,
    Cart, CartItem,
    Order, Address, BankPayment,
     OrderItem
    )
import uuid # only if you have these models
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
import json
from django.core.mail import EmailMessage
from django.utils.html import format_html
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()
import random

def home(request):
    plane_list = Plane.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    paginator = Paginator(plane_list, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html',{
        'planes': page_obj,
        'categories': categories
    })

def careers(request):
    return render(request, 'Careers.html')

def approvals(request):
    return render(request, 'approvals.html')

def airplatforms(request):
    return render(request, 'air_platforms.html')

def contact(request):
    return render(request, 'contact.html')

def fixed_wing(request):
    return render(request, 'fixed_wing.html')

def rotary_wing(request):
    return render(request, 'rotary_wings.html')

def land_platforms(request):
    return render(request, 'land_platforms.html')

def profile(request):
    return render(request, 'profile.html')

def products(request):
    plane_list = Plane.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    paginator = Paginator(plane_list, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'products.html',{
        'planes': page_obj,
        'categories': categories
    })

def cart(request):
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    items = cart.items.all() if cart else []
    return render(request, 'cart.html',{'cart': cart, 'items': items})



def checkout(request):
    """
    Display the checkout page for the current user's active cart.
    """
    # Get the active cart for the logged-in user
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()

    # Get items in the cart
    items = cart.items.all() if cart else []

    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'checkout.html', context)


def product_detail(request, id):
    # Get the plane or return 404 if it doesn't exist
    plane = get_object_or_404(Plane, id=id)
    
    return render(request, 'product-details.html', {'plane': plane})



def news(request):
    # Example if you have a News model:
    # articles = NewsArticle.objects.all()
    # return render(request, 'news.html', {'articles': articles})
    return render(request, 'news.html')



def signup(request):
    return render(request,'auth/signup.html')

def login_view(request):
    return render(request,'auth/login.html')


def password_reset(request):
    return render(request,'auth/recovery_code.html')

def reset_password_view(request):
    return render(request,'auth/Password_Reset.html')




def register_user(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method."}, status=405)

        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("contact", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # ✅ Validate required fields
        if not all([full_name, username, email, phone, password, confirm_password]):
            return JsonResponse({"error": "Please fill in all required fields."}, status=400)

        # ✅ Password match check
        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match."}, status=400)

        # ✅ Check if username or email already exists
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email is already registered."}, status=400)
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username is already taken."}, status=400)

        # ✅ Create user securely
        user = CustomUser.objects.create(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
        )

        # ✅ Hash and set password
        user.password = make_password(password)
        user.save()

        return JsonResponse({
            "message": "Account created successfully!",
            "redirect_url": "/login/"  # or use Django's reverse('login')
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    



def login_user(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method."}, status=405)

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required."}, status=400)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                "message": f"Welcome back, {user.full_name}!",
                "redirect_url": "/"  # or reverse('dashboard')
            }, status=200)
        else:
            return JsonResponse({"error": "Invalid email or password."}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    





def add_to_cart(request):
    if request.method == 'POST':
        plane_id = request.POST.get('plane_id')
        plane = get_object_or_404(Plane, id=plane_id)

        cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, plane=plane)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f'{plane.name} added to cart',
            'cart_count': cart.items.count()
        })



def update_cart_item(request):
    if request.method == 'POST':
        # Parse JSON body
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action')

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user, cart__is_paid=False)

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        elif action == 'remove':
            item.delete()

        # Get updated quantity/item total
        quantity = item.quantity if hasattr(item, 'quantity') else 0
        item_total = item.total_price if hasattr(item, 'total_price') else 0
        cart_total = item.cart.total_price if hasattr(item, 'cart') else 0

        # Optionally, cart_count for navbar
        cart_count = item.cart.items.count() if hasattr(item, 'cart') else 0

        return JsonResponse({
            'success': True,
            'quantity': quantity,
            'item_total': item_total,
            'cart_total': cart_total,
            'cart_count': cart_count
        })
    return JsonResponse({'success': False}, status=400)


def place_order_ajax(request):
    if request.method == "POST":
        user = request.user
        cart = get_object_or_404(Cart, user=user, is_paid=False)
        items = cart.items.all()

        if not items.exists():
            return JsonResponse({"status": "error", "message": "Your cart is empty."})

        # Get billing details from POST
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company_name = request.POST.get("company_name", "")
        address_line = request.POST.get("address")
        apartment = request.POST.get("apartment", "")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip")
        country = request.POST.get("country")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Create the order
        order = Order.objects.create(
            user=user,
            cart=cart,
            total_price=cart.total_price,
            is_paid=False
        )

        # Save order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                plane=item.plane,
                quantity=item.quantity,
                price=item.plane.price
            )

        # Save billing address
        Address.objects.create(
            order=order,
            first_name=first_name,
            last_name=last_name,
            company=company_name,
            address=address_line,
            apartment=apartment,
            city=city,
            state=state,
            zip_code=zip_code,
            email=email,
            phone=phone,
        )

        # Clear the items from the cart so it doesn't show again
        items.delete()

        # Get active bank payment method
        bank_payment = BankPayment.objects.filter(is_active=True).first()
        if not bank_payment:
            return JsonResponse({"status": "error", "message": "Bank payment method is not available."})

        bank_data = {
            "name": bank_payment.name,
            "bank_name": bank_payment.bank_name,
            "account_name": bank_payment.account_name,
            "account_number": bank_payment.account_number,
            "routing_number": bank_payment.routing_number,
            "instructions": bank_payment.instructions
        }

        return JsonResponse({
            "status": "success",
            "bank": bank_data,
            "order_id": order.id
        })

    return JsonResponse({"status": "error", "message": "Invalid request."})





def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    address = getattr(order, "address", None)
    bank_payment = BankPayment.objects.filter(is_active=True).first()

    return render(request, "order_success.html", {
        "order": order,
        "address": address,
        "bank": bank_payment,
    })



def orders_page(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})



def order_detail(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get billing/shipping address
    address = getattr(order, 'address', None)
    
    # Get bank payment method (active)
    bank = BankPayment.objects.filter(is_active=True).first()
    
    # Get the order items
    order_items = order.items.all()  # <-- updated to use OrderItem model

    return render(request, 'order_detail.html', {
        'order': order,
        'address': address,
        'bank': bank,
        'order_items': order_items,
    })



def contact_submit(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Basic validation
        if not (name and email and message):
            return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

        try:
          

            # Build styled email to admin
            html_message = format_html("""
                <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafc; color: #333;">
                    <h2 style="color: #004aad;">New Contact Message</h2>
                    <p><strong>Name:</strong> {}</p>
                    <p><strong>Email:</strong> {}</p>
                    <p><strong>Phone:</strong> {}</p>
                    <p><strong>Subject:</strong> {}</p>
                    <hr>
                    <p style="margin-top:10px;"><strong>Message:</strong></p>
                    <p style="background:#fff; padding:15px; border-radius:8px; border:1px solid #eee;">{}</p>
                    <hr>
                    <small>This message was submitted via the TAE Aerospace website contact form.</small>
                </div>
            """, name, email, phone, subject, message)

            # Send email
            mail = EmailMessage(
                subject=f"Contact Form: {subject or 'No Subject'}",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.ADMIN_EMAIL],  # define this in settings
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=False)

            return JsonResponse({"success": True})

        except Exception as e:
            # Log detailed errors for devs
            print("❌ Contact form error:", e)
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



# --------------------------
# Send Recovery Code View
# --------------------------
def send_recovery_code(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"success": False, "message": "Email is required."}, status=400)

        try:
            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({"success": False, "message": "No user found with that email."}, status=404)

            # Generate 6-digit recovery code
            recovery_code = str(random.randint(100000, 999999))

            # Store email and hashed code in session
            request.session["recovery_email"] = email
            request.session["recovery_code"] = make_password(recovery_code)
            request.session.modified = True  # ✅ ensure it's saved

            # Email template
            html_message = format_html(
                """
                <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafc; color: #333;">
                    <h2 style="color: #004aad;">Password Recovery Code</h2>
                    <p>Hello <strong>{}</strong>,</p>
                    <p>We received a request to reset your password.</p>
                    <p style="font-size: 18px; font-weight: bold; background:#f1f1f1; padding:10px; border-radius:8px; text-align:center;">
                        Your recovery code: <span style="color:#004aad;">{}</span>
                    </p>
                    <p>If you didn’t request this, please ignore this message.</p>
                    <br>
                    <p style="font-size:13px; color:#777;">– TAE Aerospace Support</p>
                </div>
                """,
                user.full_name,
                recovery_code,
            )

            # Send email
            mail = EmailMessage(
                subject="Your TAE Aerospace Password Recovery Code",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=False)

            return JsonResponse({
                "success": True,
                "message": "Recovery code sent successfully! Please check your email.",
            })

        except Exception as e:
            print("❌ Error sending recovery code:", e)
            return JsonResponse({"success": False, "message": "An error occurred while sending email."}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)



# --------------------------
# Reset Password View
# --------------------------
def reset_password(request):
    if request.method == "POST":
        recovery_code_input = request.POST.get("recovery_code", "").strip()
        new_password = request.POST.get("new_password", "").strip()

        # Retrieve from session
        session_email = request.session.get("recovery_email")
        session_code_hash = request.session.get("recovery_code")

        if not session_email or not session_code_hash:
            return JsonResponse({"success": False, "message": "Session expired. Please request a new recovery code."}, status=400)

        # Verify code
        if not check_password(recovery_code_input, session_code_hash):
            return JsonResponse({"success": False, "message": "Invalid recovery code."}, status=400)

        # Update password
        try:
            user = User.objects.get(email=session_email)
            user.password = make_password(new_password)
            user.save()

            # Clear session data after success
            request.session.pop("recovery_email", None)
            request.session.pop("recovery_code", None)

            return JsonResponse({
                "success": True,
                "message": "Password updated successfully! You can now log in.",
            })

        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found."}, status=404)
        except Exception as e:
            print("❌ Error resetting password:", e)
            return JsonResponse({"success": False, "message": "An error occurred while resetting password."}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)