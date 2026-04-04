from django.contrib import admin
from django.urls import path
from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Transactions
    path('add/', views.add_transaction, name='add_transaction'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),

    # Dashboard & reports
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.expense_report, name='expense_report'),


    # Order system
    path('', views.order_form, name='index'),           # Home page showing books / order form
    path('Order/', views.order, name='order'),          # Handles POST when order submitted
    path('cart/', views.cart_view, name='cart'),        # View cart / latest order
    path('cart/delete/<int:item_id>/', views.delete_item, name='delete_item'),
]
