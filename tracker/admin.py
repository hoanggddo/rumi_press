from django.contrib import admin
from tracker.models import Category, Book
from .models import Transaction  # Import the Transaction model

# No need to check if Book is registered or manually register it again

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'published_date', 'category', 'distribution_expense']
    list_filter = ['category', 'published_date']
    search_fields = ['title', 'authors']

    def get_published_date(self, obj):
        return obj.published_date.strftime('%m/%d/%Y')

    get_published_date.short_description = 'Published Date'


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'description', 'amount', 'type']
    list_filter = ['type', 'date']
    search_fields = ['description']

admin.site.register(Transaction, TransactionAdmin)  # Register the Transaction model with the admin site
