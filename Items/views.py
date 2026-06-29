from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.urls import reverse, reverse_lazy
from django.http import HttpRequest
from django.views.decorators.http import require_http_methods

from .models import (
    Category,
    Book,
    StationeryItem,
    Customer,
    Order,
    OrderItem,
)

import base64
from django.contrib.auth import get_user_model

User = get_user_model()

# For Admin
def _is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()

# For Staff
def _is_staff_user(user):
    return user.is_authenticated and user.groups.filter(name='Staff').exists()

# For Register
def register(request: HttpRequest):
    # Production-ready: uses Django forms? We'll implement minimal using User model.
    if request.method == 'POST':
        username = request.POST.get('username', '').strip() # strip for removing extra spaces
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'Staff')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('register') # redirect for send user to other page
            # exists for lastest record match with condition
        if User.objects.filter(username=username).exists():     # filter for macted with condition
            messages.error(request, 'Username already exists.') # error for message showing 
            return redirect('register') # redirect for send user to other page

        user = User.objects.create_user(username=username, email=email, password=password) # create for creating new data

        group_name = 'Admin' if role == 'Admin' else 'Staff'
        group, _ = Group.objects.get_or_create(name=group_name) # get_or_create for find data in DB
        user.groups.add(group) # add for adding objects

        messages.success(request, 'Account created. Please log in.')
        return redirect('login') # redirect for send user to other page
        # render for show html page
    return render(request, 'registration/register.html')

# For user login 
def user_login(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip() # remove extra spaces
        password = request.POST.get('password', '')
        # authenticate for check login user
        user = authenticate(request, username=username, password=password)
        if user is None: # None for nothing
            messages.error(request, 'Invalid username or password.') # error for message showing
            return redirect('login') # redirect for send user to other page

        login(request, user)
        return redirect('dashboard') # redirect for send user to other page

    return render(request, 'registration/login.html')


@login_required # Decorator
def user_logout(request: HttpRequest):
    logout(request)
    return redirect('login')  # redirect for send user to other page


@login_required  # Decorator
@user_passes_test(_is_admin)
def dashboard(request: HttpRequest):
    total_books = Book.objects.count()
    total_items = StationeryItem.objects.count()
    total_categories = Category.objects.count()  # count for counting
    total_customers = Customer.objects.count()

    total_orders = Order.objects.count()  # aggregate for perform calculation on recodes in DB
    total_sales = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
                                            # order_by for sort result
    low_stock = Book.objects.filter(quantity__lte=5).order_by('quantity')[:10] 
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
                        # select_related for fetch related objects 
    monthly_sales = (           # TruncMonth for groups dates by month
        Order.objects.annotate(month=TruncMonth('created_at'))  # annotate for new calculated field
        .values('month') # values for returns dictionaries instead of model objects
        .annotate(total=Sum('total_amount')) # annotate for new calculated field
        .order_by('month')
    )
                            # strftime for format a date or time into a string
    monthly_labels = [x['month'].strftime('%Y-%m') for x in monthly_sales if x['month']]
    monthly_values = [x['total'] for x in monthly_sales]

    context = {
        'total_books': total_books,
        'total_items': total_items,
        'total_categories': total_categories,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'monthly_labels': monthly_labels,
        'monthly_values': monthly_values,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@user_passes_test(_is_admin)
def book_list(request: HttpRequest):
    q = request.GET.get('q', '').strip()  # remove extra spaces
    category_id = request.GET.get('category', '').strip()
            # select_related for fetch related objects
    qs = Book.objects.select_related('category').all().order_by('-created_date') # order_by for sort result
    if q:   # icontains for search text in field 
        qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q) | qs.filter(isbn__icontains=q)
    if category_id:  # filter for macted with condition
        qs = qs.filter(category_id=category_id)

    paginator = Paginator(qs, 10) # split a large number of records into smaller pages
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'books': page_obj,
        'categories': Category.objects.all(), # split a large number of records into smaller pages
        'q': q,
        'category_id': category_id,
    }
    return render(request, 'books/book_list.html', context)


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def book_create(request: HttpRequest):
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', '').strip(),
            'author': request.POST.get('author', '').strip(),
            'isbn': request.POST.get('isbn', '').strip(),      # remove extra spaces
            'publisher': request.POST.get('publisher', '').strip(),
            'category_id': request.POST.get('category', '').strip() or None,
            'price': request.POST.get('price', '0'),
            'quantity': request.POST.get('quantity', '0'),
            'description': request.POST.get('description', '').strip(),
        }
        cover = request.FILES.get('cover_image')
        book = Book(**data)
        if cover:
            book.cover_image = cover
        book.save()
        messages.success(request, 'Book added.')
        return redirect('book_list')  # redirect for send user to other page
                            # all for split a large number of records into smaller pages
    return render(request, 'books/book_form.html', {'categories': Category.objects.all()})


@login_required
@user_passes_test(_is_admin)
def book_detail(request: HttpRequest, pk: int):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def book_update(request: HttpRequest, pk: int):
    book = get_object_or_404(Book, pk=pk) # get_object_or_404 for retrieve one object from the database

    if request.method == 'POST':
        book.title = request.POST.get('title', '').strip()
        book.author = request.POST.get('author', '').strip()
        book.isbn = request.POST.get('isbn', '').strip()        # remove extra spaces
        book.publisher = request.POST.get('publisher', '').strip()
        book.category_id = request.POST.get('category', '').strip() or None
        book.price = request.POST.get('price', '0')
        book.quantity = request.POST.get('quantity', '0')
        book.description = request.POST.get('description', '').strip()
        cover = request.FILES.get('cover_image')
        if cover:
            book.cover_image = cover
        book.save()
        messages.success(request, 'Book updated.')  # error for message showing
        return redirect('book_detail', pk=book.pk) # redirect for send user to other page

    return render(request, 'books/book_form.html', {'book': book, 'categories': Category.objects.all()})


@login_required
@user_passes_test(_is_admin)
def book_delete(request: HttpRequest, pk: int):
    book = get_object_or_404(Book, pk=pk) # get_object_or_404 for retrieve one object from the database
    if request.method == 'POST':
        book.delete()   # delete for remove objects 
        messages.success(request, 'Book deleted.')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


@login_required
@user_passes_test(_is_admin)
def item_list(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
                                                # order_by for sort result
    qs = StationeryItem.objects.select_related('category').all().order_by('-created_date')
    if q:    # filter for macted with condition
        qs = qs.filter(item_name__icontains=q) | qs.filter(brand__icontains=q) | qs.filter(category__name__icontains=q)
    if category_id:
        qs = qs.filter(category_id=category_id)  # filter for macted with condition

    paginator = Paginator(qs, 10)  # Paginator for show all records at once 
    page_obj = paginator.get_page(request.GET.get('page')) # get_page for get the records for one specific page

    context = {
        'items': page_obj, 
        'categories': Category.objects.all(), # Category for different types
        'q': q,
        'category_id': category_id,
    }
    return render(request, 'stationery/item_list.html', context)


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def item_create(request: HttpRequest):
    if request.method == 'POST':
        data = {
            'item_name': request.POST.get('item_name', '').strip(),
            'brand': request.POST.get('brand', '').strip(),     # remove extra spaces
            'category_id': request.POST.get('category', '').strip() or None,
            'price': request.POST.get('price', '0'),
            'quantity': request.POST.get('quantity', '0'),
            'description': request.POST.get('description', '').strip(),
        }
        image = request.FILES.get('image')
        obj = StationeryItem(**data)
        if image:
            obj.image = image
        obj.save()
        messages.success(request, 'Stationery item added.')
        return redirect('item_list')

    return render(request, 'stationery/item_form.html', {'categories': Category.objects.all()})


@login_required
@user_passes_test(_is_admin)
def item_detail(request: HttpRequest, pk: int):
    item = get_object_or_404(StationeryItem, pk=pk) # get_object_or_404 for retrieve one object from the database
    return render(request, 'stationery/item_detail.html', {'item': item})


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def item_update(request: HttpRequest, pk: int):
    item = get_object_or_404(StationeryItem, pk=pk) # get_object_or_404 for retrieve one object from the database
    if request.method == 'POST':
        item.item_name = request.POST.get('item_name', '').strip()
        item.brand = request.POST.get('brand', '').strip()    # remove extra spaces
        item.category_id = request.POST.get('category', '').strip() or None
        item.price = request.POST.get('price', '0')
        item.quantity = request.POST.get('quantity', '0')
        item.description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        if image:
            item.image = image
        item.save()
        messages.success(request, 'Stationery item updated.')
        return redirect('item_detail', pk=item.pk)

    return render(request, 'stationery/item_form.html', {'item': item, 'categories': Category.objects.all()})


@login_required
@user_passes_test(_is_admin)
def item_delete(request: HttpRequest, pk: int):
    item = get_object_or_404(StationeryItem, pk=pk) # get_object_or_404 for retrieve one object from the database
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Stationery item deleted.')
        return redirect('item_list')
    return render(request, 'stationery/item_confirm_delete.html', {'item': item})


@login_required
@user_passes_test(_is_admin)
def category_list(request: HttpRequest):
    categories = Category.objects.all().order_by('name') # order_by for sort result
    return render(request, 'categories/category_list.html', {'categories': categories})


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def category_create(request: HttpRequest):
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name', '').strip(),   # remove extra spaces
            description=request.POST.get('description', '').strip(),
        )
        messages.success(request, 'Category created.')
        return redirect('category_list')

    return render(request, 'categories/category_form.html')


@login_required
@user_passes_test(_is_admin)
@require_http_methods(['GET', 'POST'])
def category_update(request: HttpRequest, pk: int):
    category = get_object_or_404(Category, pk=pk)  # get_object_or_404 for retrieve one object from the database
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()  # remove extra spaces
        category.save()
        messages.success(request, 'Category updated.')
        return redirect('category_list')

    return render(request, 'categories/category_form.html', {'category': category})


@login_required
@user_passes_test(_is_admin)
def category_delete(request: HttpRequest, pk: int):
    category = get_object_or_404(Category, pk=pk) # get_object_or_404 for retrieve one object from the database
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'categories/category_confirm_delete.html', {'category': category})


@login_required
def password_change_view(request: HttpRequest):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'registration/password_change.html', {'form': form})


def password_reset_request(request: HttpRequest):
    # Minimal placeholder that works with Django's built-in token system would require email backend.
    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(
            request=request,
            from_email=None,
            email_template_name='registration/password_reset_email.html',
        )
        return redirect('password_reset_done')
    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done(request: HttpRequest):
    return render(request, 'registration/password_reset_done.html')

                                # unidb64 for user ID    # token for unique security string
def password_reset_confirm(request: HttpRequest, uidb64: str, token: str):
    # Uses Django's built-in mechanisms.
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64)) # urlsafe_base64_decode for reset password
        user = UserModel._default_manager.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not new_password or new_password != confirm:
                messages.error(request, 'Passwords do not match.')
                return redirect(reverse('password_reset_confirm', args=[uidb64, token]))
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('password_reset_complete')            # token for unique security string
        return render(request, 'registration/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
                                                                        # unidb64 for user ID
    messages.error(request, 'Invalid or expired reset link.')
    return redirect('password_reset_request')


def password_reset_complete(request: HttpRequest):
    return render(request, 'registration/password_reset_complete.html')


