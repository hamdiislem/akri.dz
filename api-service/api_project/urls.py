from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from cars.views import CarViewSet
from bookings.views import BookingViewSet
from reviews.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/admin/', include('admin_api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
