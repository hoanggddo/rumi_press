from django.db import models
from datetime import date
from django.contrib.auth.models import User

# Define a function that returns a default date in the correct format (YYYY-MM-DD)
def default_published_date():
    return date(2000, 1, 1)  # No need for .date() here

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name  # <-- THIS fixes it

    class Meta:
        db_table = 'tracker_category'

class Book(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    authors = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    published_date = models.DateField()
    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=1)  # <-- set default stock to 1
    distribution_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tracker_book'

        
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='expense')

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount} ({self.type})"

    class Meta:
        db_table = 'tracker_transaction'



# NEW: Order models
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending','Pending'), ('Shipped','Shipped'), ('Delivered','Delivered'), ('Cancelled','Cancelled')],
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"