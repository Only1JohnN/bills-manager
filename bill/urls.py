from django.urls import path
from .views import BillViewSet, BillStatusView, pay_bill


urlpatterns = [
    #Bill API URLs
    path('', BillViewSet.as_view({'get': 'list', 'post': 'create'}), name='bill-home'),
    path('<int:pk>/', BillViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='bill-detail'),
    path('bills/<int:bill_id>/pay/', pay_bill, name='pay-bill'),
    
    #Status API URLs
    path('status/', BillStatusView.as_view(), name='bill-status'),
]