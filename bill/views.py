from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import Bill
from .serializers import BillSerializer
from .pagination import CustomBillPagination
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class BillsListViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing bill instances.
    """
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    pagination_class = CustomBillPagination  # Use the custom pagination class
    
    def get_queryset(self):
        """
        Optionally restricts the returned bills to the authenticated user.
        """
        user = self.request.user
        return Bill.objects.filter(user=user)

    def perform_create(self, serializer):
        # Assign the authenticated user to the bill
        serializer.save(user=self.request.user)
        

class BillStatusView(APIView):
    def get(self, request):
        today = now().date()
        return Response({
            # "upcoming": BillSerializer(Bill.objects.filter(due_date__gte=today, is_paid=False), many=True).data,
            # "overdue": BillSerializer(Bill.objects.filter(due_date__lt=today, is_paid=False), many=True).data,
            # "recurring": BillSerializer(Bill.objects.exclude(repeat_frequency=Bill.RepeatFrequency.DO_NOT_REPEAT), many=True).data,
            # "paid": BillSerializer(Bill.objects.filter(is_paid=True), many=True).data,
            
            "upcoming": BillSerializer(Bill.objects.filter(due_date__gte=today), many=True).data,
            "overdue": BillSerializer(Bill.objects.filter(due_date__lt=today), many=True).data,
            "recurring": BillSerializer(Bill.objects.exclude(repeat_frequency=Bill.RepeatFrequency.DO_NOT_REPEAT), many=True).data,
            "paid": BillSerializer(Bill.objects.filter(), many=True).data,
        })


@api_view(['POST'])
def pay_bill(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id, user=request.user)  # make sure user owns the bill
    except Bill.DoesNotExist:
        return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)

    if bill.is_paid:
        return Response({'message': 'Bill is already paid'}, status=status.HTTP_400_BAD_REQUEST)

    # Logic to process payment would go here (integrate with wallet/payment gateway)

    # Mark as paid
    bill.is_paid = True
    bill.paid_at = now()
    bill.save()

    return Response({'message': 'Bill marked as paid'}, status=status.HTTP_200_OK)
