from django import forms
from .models import Category, Book, Transaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['id','title', 'subtitle', 'authors', 'publisher', 'published_date', 'category', 'distribution_expense']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'date', 'description']