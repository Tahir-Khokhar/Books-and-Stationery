from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=30, unique=True)
    publisher = models.CharField(max_length=200, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta: # Meta for ordering time/time when you order
        ordering = ["-created_date"] 

    def __str__(self):
        return self.title


class StationeryItem(models.Model):
    item_name = models.CharField(max_length=150)
    brand = models.CharField(max_length=150, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='stationery_items')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='stationery/', blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.item_name


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_username()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')

    created_at = models.DateTimeField(auto_now_add=True)

    # simple totals
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # could be either book or stationery. Keep both nullable.
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    stationery_item = models.ForeignKey(StationeryItem, on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.book_id:
            self.unit_price = self.book.price
        elif self.stationery_item_id:
            self.unit_price = self.stationery_item.price

        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

