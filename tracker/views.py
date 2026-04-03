# tracker/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Book, Transaction, Order, OrderItem
from .forms import CategoryForm, BookForm
from django.db.models import Sum, Count, Max
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
@login_required
def index(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Show latest order if redirected from submit_order
    latest_order = None
    latest_order_id = request.session.pop('latest_order_id', None)
    if latest_order_id:
        try:
            latest_order = Order.objects.get(id=latest_order_id)
        except Order.DoesNotExist:
            latest_order = None

    context = {
        'transactions': transactions,
        'latest_order': latest_order,
        'books': Book.objects.all()  # for the table in home page
    }
    return render(request, 'tracker/index.html', context)

@login_required   
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.stock > 0:
        book.stock -= 1
        book.save()

    return redirect('book_list')
@login_required
def delete_category(request, category_id):
    # Get the category object to delete
    category = get_object_or_404(Category, id=category_id)
    
    # Delete the category
    category.delete()
    
    # Redirect back to the category list view
    return redirect('category_list')
# Render category list
def category_list(request):
    categories = Category.objects.annotate(
        total_expense=Sum('books__distribution_expense'),
        book_count=Count('books')
    )
    return render(request, 'tracker/category_list.html', {
        'categories': categories
    })
@login_required
# Handle adding a new category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'tracker/add_category.html', {'form': form})

# Render book list
def book_list(request):
    query = request.GET.get('q', '')  # Search query
    category_id = request.GET.get('category', '')  # Category filter

    books = Book.objects.all()

    if query:
        books = books.filter(
            title__icontains=query
        ) | books.filter(
            authors__icontains=query
        )

    if category_id:
        books = books.filter(category_id=category_id)

    categories = Category.objects.all()
    context = {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'tracker/book_list.html', context)


@login_required
# Handle adding a new book
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            new_book = form.save(commit=False)

            # Check if a similar book already exists
            existing_book = Book.objects.filter(
                title=new_book.title,
                authors=new_book.authors
            ).first()

            if existing_book:
                # Increase stock instead of creating new book
                existing_book.stock += new_book.stock
                existing_book.save()
            else:
                # Save as new book
                new_book.save()

            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'tracker/add_book.html', {'form': form})
@login_required
def submit_order(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_ids')
        if book_ids:
            order = Order.objects.create(user=request.user)
            for book_id in book_ids:
                book = Book.objects.get(id=book_id)
                quantity = int(request.POST.get(f'quantity_{book_id}', 1))
                if book.stock >= quantity:
                    OrderItem.objects.create(order=order, book=book, quantity=quantity)
                    book.stock -= quantity
                    book.save()
                else:
                    messages.error(request, f"Not enough stock for {book.title}")
            request.session['latest_order_id'] = order.id  # store order ID in session
        else:
            messages.error(request, "No books selected.")
    return redirect('home')  # redirect to home page after order submission
@login_required
def cart_view(request):
    # Get the user's current "Pending" order or create one
    latest_order, created = Order.objects.get_or_create(user=request.user, status='Pending')
    
    # Calculate totals
    total_books = sum(item.quantity for item in latest_order.items.all())
    total_price = sum(item.quantity * item.book.distribution_expense for item in latest_order.items.all())

    return render(request, 'tracker/cart.html', {
        'latest_order': latest_order,
        'total_books': total_books,
        'total_price': total_price,
    })
@login_required
def order(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_ids')

        # Get first pending order, or create one
        pending_orders = Order.objects.filter(user=request.user, status='Pending')
        latest_order = pending_orders.first()
        if not latest_order:
            latest_order = Order.objects.create(user=request.user, status='Pending')

        # Optional: merge duplicate pending orders
        for order in pending_orders[1:]:
            for item in order.items.all():
                existing_item = latest_order.items.filter(book=item.book).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.order = latest_order
                    item.save()
            order.delete()

        # Add new items to the latest_order
        for book_id in book_ids:
            book = get_object_or_404(Book, id=book_id)
            quantity = int(request.POST.get(f'quantity_{book.id}', 1))

            order_item, created = OrderItem.objects.get_or_create(order=latest_order, book=book)
            if not created:
                order_item.quantity += quantity
            else:
                order_item.quantity = quantity
            order_item.save()

            # Reduce stock
            book.stock -= quantity
            book.save()

        return redirect('cart')
    else:
        return redirect('index')

@login_required
def order_form(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(title__icontains=query) | books.filter(authors__icontains=query)

    latest_order = None  # for showing summary
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_ids')
        if book_ids:
            order = Order.objects.create(user=request.user)
            for book_id in book_ids:
                book = Book.objects.get(id=book_id)
                quantity = int(request.POST.get(f'quantity_{book_id}', 1))
                if book.stock >= quantity:
                    OrderItem.objects.create(order=order, book=book, quantity=quantity)
                    book.stock -= quantity
                    book.save()
                else:
                    messages.error(request, f"Not enough stock for {book.title}")
            latest_order = order  # save to pass to template

    return render(request, 'tracker/index.html', {
        'books': books,
        'query': query,
        'latest_order': latest_order
    })

@login_required
# Generate expense report for categories and their books
def expense_report(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    }
    return render(request, 'tracker/expense_report.html', context)
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # Associate the transaction with the logged-in user
            transaction.save()
            return redirect('expense_report')  # Redirect to the expense report page after adding a transaction
    else:
        form = TransactionForm()
    context = {
        'form': form
    }
    return render(request, 'tracker/add_transaction.html', context)

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    
    # Restore stock
    book = item.book
    book.stock += item.quantity
    book.save()
    
    # Delete the item from the order
    item.delete()
    
    return redirect('cart')  # Redirect back to cart page


@login_required
def cart_view(request):
    # Get the latest order for the logged-in user
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()

    total_books = 0
    total_price = 0

    if latest_order:
        # Use 'items' because of related_name in OrderItem
        for item in latest_order.items.all():
            item.subtotal = item.quantity * item.book.distribution_expense  # or item.book.price if you have a price field
            total_books += item.quantity
            total_price += item.subtotal

    context = {
        'latest_order': latest_order,
        'total_books': total_books,
        'total_price': total_price,
    }

    return render(request, 'tracker/cart.html', context)
    
@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('expense_report')  # Redirect to the expense report page after editing a transaction
    else:
        form = TransactionForm(instance=transaction)
    context = {
        'form': form,
    }
    return render(request, 'tracker/edit_transaction.html', context)

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('expense_report')  # Redirect to the expense report page after deleting a transaction
    context = {
        'transaction': transaction,
    }
    return render(request, 'tracker/delete_transaction.html', context)

@login_required
def dashboard(request):
    # Get all transactions for the user
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # KPI calculations
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Books and categories for dashboard tables
    books = Book.objects.all()
    categories = Category.objects.all()

    # Expense by category
    category_summary = categories.annotate(
        total_expense=Sum('books__distribution_expense'),
        book_count=Count('books')
    )

    # Expense trends over time (group by date)
    expense_trends = (
        transactions.filter(type='expense')
        .values('date')
        .annotate(total_expense=Sum('amount'))
        .order_by('date')
    )

    # Highest expense category
    highest_expense_category_obj = category_summary.order_by('-total_expense').first()
    highest_expense_category = highest_expense_category_obj.name if highest_expense_category_obj else 'N/A'

    # Book with highest distribution cost
    highest_cost_book_obj = books.order_by('-distribution_expense').first()
    highest_cost_book = highest_cost_book_obj if highest_cost_book_obj else None

    # Handle filtering from dashboard (optional)
    selected_category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    filtered_books = books
    if selected_category_id:
        filtered_books = filtered_books.filter(category_id=selected_category_id)
    if start_date:
        filtered_books = filtered_books.filter(date__gte=start_date)
    if end_date:
        filtered_books = filtered_books.filter(date__lte=end_date)

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'books': filtered_books,
        'categories': categories,
        'category_summary': category_summary,
        'expense_trends': expense_trends,
        'highest_expense_category': highest_expense_category,
        'highest_cost_book': highest_cost_book,
        'selected_category': selected_category_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'tracker/dashboard.html', context)

# nope
from django.contrib.auth.models import User
from django.http import HttpResponse

def reset_admin_password(request):
    # Replace with your admin username
    username = 'hoanggddo'
    new_password = 'Tanisgay123'

    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return HttpResponse("Password reset successfully!")
    except User.DoesNotExist:
        return HttpResponse("Admin user not found.")

