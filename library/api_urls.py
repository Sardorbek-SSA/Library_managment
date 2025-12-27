from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .api_views import *

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'borrows', BorrowViewSet, basename='borrow')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'reviews', ReviewViewSet, basename='review')

schema_view = get_schema_view(
    openapi.Info(
        title="Library API",
        default_version='v1',
        description="Library Management System API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', TokenObtainPairView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Main resources
    path('', include(router.urls)),
    
    # Actions
    path('return/<int:borrow_id>/', ReturnBookView.as_view(), name='api_return'),
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    path('statistics/', StatisticsView.as_view(), name='api_stats'),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]