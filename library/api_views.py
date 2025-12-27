from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Book, Borrow, Reservation, Review
from .serializers import *

# Permissions
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

# Auth Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password='temp_password'  # Frontend parolni yuboradi
        )
        return user

# Book Views
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'description']
    filterset_fields = ['available', 'author']
    ordering_fields = ['title', 'author']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStaff()]
        return [AllowAny()]

# Borrow Views
class BorrowViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Borrow.objects.all()
        return Borrow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        if not book.available:
            raise serializers.ValidationError("Book not available")
        
        book.available = False
        book.save()
        
        serializer.save(
            user=self.request.user,
            due_date=timezone.now().date() + timedelta(days=14)
        )

# Reservation Views
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Review Views
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Return Book View
class ReturnBookView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, borrow_id):
        try:
            borrow = Borrow.objects.get(id=borrow_id)
            
            # Check permission
            if not request.user.is_staff and borrow.user != request.user:
                return Response({"error": "Permission denied"}, status=403)
            
            if borrow.returned:
                return Response({"error": "Already returned"}, status=400)
            
            borrow.returned = True
            borrow.save()
            
            # Make book available
            book = borrow.book
            book.available = True
            book.save()
            
            return Response({"message": "Book returned successfully"})
        except Borrow.DoesNotExist:
            return Response({"error": "Borrow not found"}, status=404)

# User Profile
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# Statistics
class StatisticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsStaff]
    
    def get(self, request):
        stats = {
            'total_books': Book.objects.count(),
            'available_books': Book.objects.filter(available=True).count(),
            'total_borrows': Borrow.objects.count(),
            'active_borrows': Borrow.objects.filter(returned=False).count(),
            'total_users': User.objects.count(),
            'total_reviews': Review.objects.count(),
        }
        return Response(stats)