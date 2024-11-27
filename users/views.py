#views.py
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, ServiceCategory, ServiceItem, Cart, CartItem , Order, OrderItem
import logging
logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'registration/home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact_number = request.POST.get('contact_number')
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        city=request.POST['city']
        gender = request.POST.get('gender')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Please use a different email.")
            return redirect('register')
        
        user = CustomUser.objects.create_user(username=username, email=email, password=password, contact_number=contact_number, first_name=first_name, last_name=last_name, city=city, gender=gender)
        user.save()
        send_mail(
    'Welcome to Event Management!',
    f'Thank you for registering, {user.username}!\n\n'
    'We are excited to have you with us and are looking forward to providing you with an excellent experience.\n\n'
    'If you have any questions or need assistance, feel free to reach out. We are here to help!\n\n'
    'Thank you once again for joining us. We hope you have a great time!\n\n'
    'Best regards,\n'
    'Event Management Team.',
    settings.EMAIL_HOST_USER,  # From email
    [user.email],  # To email
    fail_silently=False,
)

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')
    
    return render(request, 'registration/register.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Send login notification email
            send_mail(
    'Login Notification',
    f'Hello {user.username},\n\n'
    'We wanted to let you know that your login to the Event Management system was successful.\n\n'
    'If you did not initiate this login, please take immediate action to secure your account. You can reset your password or contact support for assistance.\n\n'
    'Thank you for using our service. We are here to assist you with anything you need!\n\n'
    'Best regards,\n'
    'Event Management Team.',
    'jayanibv@gmail.com',
    [user.email],
    fail_silently=False,
)

            messages.success(request, 'Login successful!')
            return redirect('home')  # Redirect to your home/dashboard page
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')  # Redirect back to the login page
    
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('login')  # Redirect to login or home

def services_view(request):
    categories = ServiceCategory.objects.prefetch_related('items').all()  # Prefetch related items
    return render(request, 'registration/services.html', {'categories': categories})

import logging
logger = logging.getLogger(__name__)
@login_required
def add_to_cart(request, item_id):
    logger.info(f"Request user: {request.user} (Authenticated: {request.user.is_authenticated})")
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to add items to your cart.")
        logger.warning("Unauthenticated user tried to add an item to the cart.")
        return redirect('login') 
    logger.info(f"Received item_id: {item_id}")
    item = get_object_or_404(ServiceItem, id=item_id)
    logger.info(f"Retrieved item: {item.name} (ID: {item.id})")
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1  # Increment quantity if already in the cart
        cart_item.save()
    cart_item.save()
    messages.success(request, f"{item.name} has been added to your cart.")
    return redirect('cart')

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.cartitem_set.all() if cart else []
    total_price = sum(item.quantity * item.item.price for item in cart_items)
    return render(request, 'registration/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def flower_view(request):
    service_items = ServiceItem.objects.filter(image__isnull=False)
    service_items = ServiceItem.objects.filter(service_type='flower_decoration')
    return render(request, 'registration/flower_decoration.html', {'service_items': service_items})

def catering_view(request):
    service_items = ServiceItem.objects.filter(service_type='catering', image__isnull=False)
    return render(request, 'registration/catering.html', {'service_items': service_items})

@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == 'POST':
        cart_item.quantity = int(request.POST.get('quantity', 1))
        cart_item.save()
        messages.success(request, f"Updated {cart_item.item.name} quantity.")
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.item.name} has been removed from your cart.")
    return redirect('cart')

def checkout(request):
    return redirect('home')

@login_required
def order_confirmation(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-date_ordered').first()
    if not latest_order:
        messages.error(request, "No recent order found.")
        return redirect('home')  # Redirect to a relevant page, such as the homepage

    # Render the confirmation page with the latest order
    return render(request, 'registration/order_confirmation.html', {'order': latest_order})

@login_required
def place_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.cartitem_set.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    cart_items = cart.cartitem_set.all()
    total_price = sum(item.quantity * item.item.price for item in cart_items)

    order = Order.objects.create(user=request.user, total_price=total_price)

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            service_item=cart_item.item,
            quantity=cart_item.quantity
        )
    
    cart.cartitem_set.all().delete()

    send_mail(
    'Order Confirmation',
    f'Hello {order.user.username},\n\n'
    'Thank you for your order! We are excited to confirm that your order has been successfully placed.\n\n'
    f'Your Order ID is: {order.id}.\n\n'
    'We are currently processing your order and will notify you once it is shipped. In the meantime, feel free to contact us for any questions or assistance regarding your order.\n\n'
    'Thank you for choosing our service! We look forward to serving you again soon.\n\n'
    'Best regards,\n'
    'Event Management Team.',
    settings.DEFAULT_FROM_EMAIL,
    [order.user.email],
    fail_silently=False,
)


    messages.success(request, "Your order has been placed successfully!")
    return redirect('cart_payment_page') 

@login_required
def cart_payment_page(request):
    """
    View to handle payment for cart items.
    """
    try:
        # Retrieve the latest order for the user
        latest_order = Order.objects.filter(user=request.user).order_by('-date_ordered').first()
        if not latest_order:
            messages.error(request, "No recent order found. Please place an order first.")
            return redirect('cart')

        # Use the total price from the order for consistency
        total_price = sum(item.quantity * item.service_item.price for item in latest_order.order_items.all())
        order_items = latest_order.order_items.all()  # Corrected related name for accessing order items
    except Order.DoesNotExist:
        messages.error(request, "There was an issue retrieving your order. Please try again.")
        return redirect('cart')

    if request.method == "POST":
        # Get selected payment method
        payment_method = request.POST.get("payment_method")
        if payment_method == "credit_card":
            # Handle credit card payment
            card_number = request.POST.get("card_number")
            expiry_date = request.POST.get("expiry_date")
            cvv = request.POST.get("cvv")

            if not all([card_number, expiry_date, cvv]):
                messages.error(request, "Incomplete credit card details.")
                return redirect("cart_payment_page")

            # Simulate successful payment
            latest_order.payment_status = 'Paid'
            latest_order.save()
            messages.success(request, "Payment successful using Credit Card!")
            return redirect('order_confirmation')

        elif payment_method == "cod":
            # Handle Cash on Delivery (COD)
            latest_order.payment_status = 'COD'
            latest_order.save()
            messages.success(request, "Order placed successfully. Please pay on delivery.")
            return redirect('order_confirmation')

        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect("cart_payment_page")

    # Render the payment page with order details
    context = {
        "order_items": order_items,
        "total_price": total_price,
        "order_id": latest_order.id,
    }
    return render(request, "registration/payment_cart.html", context)

@login_required
def checkout_cart(request):
    """
    Checkout view for cart items.
    """
    cart_items = Cart.objects.filter(user=request.user)
    if cart_items.exists():
        return redirect('cart_payment_page')
    else:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

