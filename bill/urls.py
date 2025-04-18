from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import BillViewSet


urlpatterns = [
    #Bill API URLs
    path('', BillViewSet.as_view({'get': 'list', 'post': 'create'}), name='bill-home'),
    
    #Token authentication URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]