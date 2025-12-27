from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Borrow, Reservation, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class BookSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews:
            return sum([r.rating for r in reviews]) / len(reviews)
        return 0

class BorrowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = Borrow
        fields = '__all__'
        read_only_fields = ['user', 'borrowed_date', 'returned']

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['user', 'reserved_date']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']