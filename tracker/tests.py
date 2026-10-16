from django.test import TestCase, Client, override_settings
from django.core import mail
from urllib.parse import urlsplit
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
        self.assertTemplateUsed(response, "account/password_reset_unavailable.html")
        self.assertContains(response, "temporarily unavailable")

    def test_password_reset_post_is_disabled_by_default(self):
        response = self.client.post(
            reverse("account_reset_password"),
            {"email": "reader@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/password_reset_unavailable.html")

    def test_password_reset_done_page_loads(self):
        response = self.client.get(reverse("account_reset_password_done"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/password_reset_done.html")
        self.assertContains(response, "Check your inbox")

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_login_page_hides_password_reset_when_disabled(self):
        response = self.client.get(reverse("account_login"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Forgot your password?")
        self.assertContains(response, reverse("account_signup"))
        self.assertNotContains(
            response,
            "Use the password reset button below if you cannot sign in.",
        )

    def test_public_signup_creates_nonstaff_user(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "customeruser",
                "email": "customer@example.com",
                "password1": "Customer-password-123!",
                "password2": "Customer-password-123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="customeruser")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_customer_cannot_manage_catalog_or_finances(self):
        customer = User.objects.create_user(
            username="customer",
            password="test-password",
        )
        category = Category.objects.create(name="Customer category")
        book = Book.objects.create(
            title="Customer Book",
            authors="Author",
            publisher="Publisher",
            published_date=date(2024, 1, 1),
            category=category,
            stock=4,
            distribution_expense=3,
        )
        self.client.force_login(customer)

        denied_responses = [
            self.client.post(reverse("add_book"), {}),
            self.client.post(reverse("add_category"), {"name": "Blocked"}),
            self.client.post(reverse("delete_book", args=[book.id]), {}),
            self.client.post(reverse("delete_category", args=[category.id]), {}),
            self.client.get(reverse("dashboard")),
            self.client.get(reverse("expense_report")),
        ]

        for response in denied_responses:
            self.assertEqual(response.status_code, 302)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Book.objects.get(pk=book.pk).stock, 4)

    def test_customer_catalog_pages_hide_management_actions(self):
        customer = User.objects.create_user(
            username="catalogcustomer",
            password="test-password",
        )
        category = Category.objects.create(name="Public category")
        Book.objects.create(
            title="Public book",
            authors="Author",
            publisher="Publisher",
            published_date=date(2024, 1, 1),
            category=category,
            stock=4,
            distribution_expense=3,
        )
        self.client.force_login(customer)

        book_response = self.client.get(reverse("book_list"))
        category_response = self.client.get(reverse("category_list"))

        self.assertNotContains(book_response, "Add Book")
        self.assertNotContains(book_response, "Delete")
        self.assertNotContains(book_response, "Expense")
        self.assertNotContains(book_response, "$3.00")
        self.assertNotContains(category_response, "Add Category")
        self.assertNotContains(category_response, "Delete")
        self.assertNotContains(category_response, "Total Expense")
        self.assertNotContains(category_response, "$3.00")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        PASSWORD_RESET_ENABLED=True,
    )
    def test_password_reset_request_sends_email(self):
        user = User.objects.create_user(
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

        reset_url = next(
            line for line in mail.outbox[0].body.splitlines()
            if line.startswith("http://testserver/accounts/password/reset/key/")
        )
        reset_response = self.client.get(urlsplit(reset_url).path, follow=True)
        self.assertEqual(reset_response.status_code, 200)
        self.assertTemplateUsed(
            reset_response,
            "account/password_reset_from_key.html",
        )
        self.assertContains(reset_response, "Choose a new password")

        change_response = self.client.post(
            urlsplit(reset_response.redirect_chain[-1][0]).path,
            {
                "password1": "Rumi-Reset-2026!Sage",
                "password2": "Rumi-Reset-2026!Sage",
            },
            follow=True,
        )
        self.assertEqual(change_response.status_code, 200)
        self.assertTemplateUsed(
            change_response,
            "account/password_reset_from_key_done.html",
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password("Rumi-Reset-2026!Sage"))

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
        EMAIL_HOST="",
        PASSWORD_RESET_ENABLED=True,
    )
    def test_password_reset_request_without_smtp_does_not_error(self):
        User.objects.create_user(
            username="localrecoveryuser",
            email="localreader@example.com",
            password="test-password",
        )

        response = self.client.post(
            reverse("account_reset_password"),
            {"email": "localreader@example.com"},
        )

        self.assertEqual(response.status_code, 302)

    def test_category_page_loads(self):
        response = self.client.get(reverse("category_list"))
        self.assertIn(response.status_code, [200, 302])

    def test_books_page_loads(self):
        response = self.client.get(reverse("book_list"))
        self.assertIn(response.status_code, [200, 302])

    def test_dashboard_page(self):
        response = self.client.get(reverse("dashboard"))
        self.assertIn(response.status_code, [200, 302])

    def test_homepage_shows_intro_to_logged_out_visitors(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracker/intro.html")
        self.assertContains(response, "Manage your book catalogue")
        self.assertContains(response, reverse("account_login"))
        self.assertContains(response, reverse("account_signup"))

    def test_admin_can_open_user_creation_page(self):
        admin_user = User.objects.create_superuser(
            username="siteadmin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        response = self.client.get("/admin/auth/user/add/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add user")

    def test_homepage_keeps_order_form_for_authenticated_visitors(self):
        user = User.objects.create_user(username="homeuser", password="12345")
        self.client.force_login(user)

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracker/index.html")
