from django.urls import path
from .views import BillsViewSet, BillStatusView


urlpatterns = [
    #Bill API URLs
    path('bills/', BillsViewSet.as_view({'get': 'list', 'post': 'create'}), name='bill-home'),
    path('bills/<int:pk>/', BillsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='bill-detail'),
    
    #Status API URLs
    path('status/', BillStatusView.as_view(), name='bill-status'),
]