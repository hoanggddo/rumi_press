from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import date

from .models import Category, Book, Transaction, Order, OrderItem


class CategoryTests(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name="Fiction")
        self.assertEqual(str(category), "Fiction")


class BookTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Science")

    def test_create_book(self):
        book = Book.objects.create(
            title="Physics 101",
            authors="John Doe",
            publisher="MIT Press",
            published_date=date(2020, 1, 1),
            category=self.category,
            stock=5,
            distribution_expense=10.50
        )

        self.assertEqual(book.title, "Physics 101")
        self.assertEqual(book.category.name, "Science")
        self.assertEqual(book.stock, 5)


class TransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            user=self.user,
            date=date.today(),
            description="Book sale",
            amount=100,
            type="income"
        )

        self.assertEqual(transaction.type, "income")
        self.assertEqual(transaction.amount, 100)


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="12345")
        self.category = Category.objects.create(name="Tech")

        self.book = Book.objects.create(
            title="Django Guide",
            authors="Dev",
            publisher="O'Reilly",
            published_date=date(2021, 1, 1),
            category=self.category,
            stock=3,
            distribution_expense=5
        )

    def test_create_order_and_item(self):
        order = Order.objects.create(user=self.user, status="Pending")

        item = OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=2
        )

        self.assertEqual(order.status, "Pending")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.book.title, "Django Guide")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_category_page_loads(self):
        response = self.client.get("/categories/")
        self.assertIn(response.status_code, [200, 302])

    def test_books_page_loads(self):
        response = self.client.get("/books/")
        self.assertIn(response.status_code, [200, 302])

    def test_dashboard_page(self):
        response = self.client.get("/dashboard/")
        self.assertIn(response.status_code, [200, 302])
