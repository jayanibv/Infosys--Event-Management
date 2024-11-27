#models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username=models.CharField(max_length=100, unique=True)
    contact_number = models.CharField(max_length=15, blank=True,null=True)
    city = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=30) 
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, blank=True, null=True)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('moderator', 'Moderator'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class ServiceItem(models.Model):
    SERVICE_CHOICES = [
        ('flower_decoration', 'Flower Decoration'),
        ('catering', 'Catering'),
    ]
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="Nothing available, error!")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=5)  # optional, for ratings
    image = models.ImageField(upload_to='items_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(ServiceItem, through='CartItem')
    def total_price(self):
        return sum(cart_item.total_price() for cart_item in self.cartitem_set.all())

    def __str__(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def total_price(self):
        return self.quantity * self.item.price

    def clean(self):
        if self.quantity < 1:
            raise ValidationError('Quantity must be at least 1.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def total_price(self):
        return self.quantity * self.item.price
    def __str__(self):
        return f"{self.cart.user.username} - {self.item.name} x {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('cod', 'Cash on Delivery'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Order {self.order.id} - {self.quantity} x {self.service_item.name}"
