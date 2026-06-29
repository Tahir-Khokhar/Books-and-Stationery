from django.urls import path
from . import views

urlpatterns = [

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # password option
    path('password-change/', views.password_change_view, name='password_change'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    # Dashboard + CRUD
    path('', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_add'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_update, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # stationery path
    path('stationery/', views.item_list, name='item_list'),
    path('stationery/add/', views.item_create, name='item_add'),
    path('stationery/<int:pk>/', views.item_detail, name='item_detail'),
    path('stationery/<int:pk>/edit/', views.item_update, name='item_edit'),
    path('stationery/<int:pk>/delete/', views.item_delete, name='item_delete'),

    # categories path
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Categories list-only endpoint (optional)
    # path('categories/<int:pk>/', views.category_detail, name='category_detail'),
]

