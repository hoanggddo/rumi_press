from django.test import TestCase, Client, override_settings
from django.core import mail
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse

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

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse("account_reset_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/forgot_pass.html")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_request_sends_email(self):
        User.objects.create_user(
            username="recoveryuser",
            email="reader@example.com",
            password="test-password",
        )

        response = self.client.post(
            reverse("account_reset_password"),
            {"email": "reader@example.com"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reader@example.com", mail.outbox[0].to)

    def test_category_page_loads(self):
        response = self.client.get(reverse("category_list"))
        self.assertIn(response.status_code, [200, 302])

    def test_books_page_loads(self):
        response = self.client.get(reverse("book_list"))
        self.assertIn(response.status_code, [200, 302])

    def test_dashboard_page(self):
        response = self.client.get(reverse("dashboard"))
        self.assertIn(response.status_code, [200, 302])
