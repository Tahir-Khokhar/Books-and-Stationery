from django import forms

from .models import Book, Category, StationeryItem


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'isbn',
            'publisher',
            'category',
            'price',
            'quantity',
            'description',
            'cover_image',
        ]


class StationeryItemForm(forms.ModelForm):
    class Meta:
        model = StationeryItem
        fields = [
            'item_name',
            'brand',
            'category',
            'price',
            'quantity',
            'description',
            'image',
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

