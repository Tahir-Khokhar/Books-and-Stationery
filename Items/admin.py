from django.contrib import admin

from .models import Category, Book, StationeryItem, Customer, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'publisher', 'category', 'price', 'quantity', 'created_date')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'isbn', 'publisher')


@admin.register(StationeryItem)
class StationeryItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'brand', 'category', 'price', 'quantity', 'created_date')
    list_filter = ('category',)
    search_fields = ('item_name', 'brand')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'total_amount')
    list_filter = ('created_at',)
    search_fields = ('customer__user__username',)
    inlines = [OrderItemInline]

