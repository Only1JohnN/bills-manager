from rest_framework import viewsets
from .models import Bill
from .serializers import BillSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class BillViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing bill instances.
    """
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def perform_create(self, serializer):
        # Assign the authenticated user to the bill
        serializer.save(user=self.request.user)

# Create your views here.

    # def perform_update(self, serializer):
    #     serializer.save(user=self.request.user)
    # def perform_destroy(self, instance):
    #     instance.delete()
    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned bills to a given user,
    #     by filtering against a `username` query parameter in the URL.
    #     """
    #     queryset = Bill.objects.all()
    #     user = self.request.query_params.get('user', None)
    #     if user is not None:
    #         queryset = queryset.filter(user__username=user)
    #     return queryset
    # def get_object(self):
    #     """
    #     Optionally restricts the returned bill to a given user,
    #     by filtering against a `username` query parameter in the URL.
    #     """
    #     queryset = Bill.objects.all()
    #     user = self.request.query_params.get('user', None)
    #     if user is not None:
    #         queryset = queryset.filter(user__username=user)
    #     return super().get_object()