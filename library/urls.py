from django.urls import path, include
from . import views

urlpatterns = [
    # HTML Frontend
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('borrow/<int:pk>/', views.borrow_book, name='borrow_book'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('add-book/', views.add_book, name='add_book'),
    
    # API
    path('api/', include('library.api_urls')),
]