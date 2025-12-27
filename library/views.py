from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Book, Borrow

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

def home(request):
    books = Book.objects.filter(available=True)[:6]
    return render(request, 'home.html', {'books': books})

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.available:
        messages.error(request, 'This book is not available')
        return redirect('book_detail', pk=pk)
    existing = Borrow.objects.filter(user=request.user, book=book, returned=False).exists()
    if existing:
        messages.warning(request, 'You already have this book')
        return redirect('book_detail', pk=pk)
    Borrow.objects.create(
        user=request.user,
        book=book,
        due_date=timezone.now().date() + timedelta(days=14)
    )
    book.available = False
    book.save()
    messages.success(request, f'You borrowed "{book.title}"')
    return redirect('my_books')

@login_required
def return_book(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)
    if borrow.user != request.user:
        messages.error(request, 'This is not your book')
        return redirect('my_books')
    if borrow.returned:
        messages.warning(request, 'Book already returned')
        return redirect('my_books')
    borrow.returned = True
    borrow.save()
    book = borrow.book
    book.available = True
    book.save()
    messages.success(request, f'You returned "{book.title}"')
    return redirect('my_books')

@login_required
def my_books(request):
    borrows = Borrow.objects.filter(user=request.user, returned=False)
    return render(request, 'my_books.html', {'borrows': borrows})

@login_required
def add_book(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add books')
        return redirect('home')
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        isbn = request.POST['isbn']
        Book.objects.create(title=title, author=author, isbn=isbn, available=True)
        messages.success(request, 'Book added successfully')
        return redirect('book_list')
    return render(request, 'add_book.html')