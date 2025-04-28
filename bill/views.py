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
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

# Create your views here.


class BillsViewSet(viewsets.ModelViewSet):
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)

        filter_type = request.query_params.get('filter_type', 'monthly')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        date_filter_upcoming = Q()
        date_filter_overdue = Q()
        date_filter_paid = Q()

        if filter_type == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            date_filter_upcoming = Q(due_date__range=(start_date, end_date))
            date_filter_overdue = Q(due_date__range=(start_date, end_date))
            date_filter_paid = Q(payment_date__date__range=(start_date, end_date))
        elif filter_type == 'bi_weekly':
            # Assuming bi-weekly starts on Mondays relative to a fixed point
            reference_date = timezone.datetime(2025, 4, 21).date()  # Example reference date
            delta = (today - reference_date).days % 14
            start_date = today - timedelta(days=delta)
            end_date = start_date + timedelta(days=13)
            date_filter_upcoming = Q(due_date__range=(start_date, end_date))
            date_filter_overdue = Q(due_date__range=(start_date, end_date))
            date_filter_paid = Q(payment_date__date__range=(start_date, end_date))
        elif filter_type == 'monthly':
            date_filter_upcoming = Q(due_date__month=today.month, due_date__year=today.year)
            date_filter_overdue = Q(due_date__month=today.month, due_date__year=today.year)
            date_filter_paid = Q(payment_date__month=today.month, payment_date__year=today.year)
        elif start_date_str and end_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                date_filter_upcoming = Q(due_date__range=(start_date, end_date))
                date_filter_overdue = Q(due_date__range=(start_date, end_date))
                date_filter_paid = Q(payment_date__date__range=(start_date, end_date))
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        upcoming_bills = Bill.objects.filter(user=user, due_date__gte=today, is_paid=False).filter(date_filter_upcoming)
        overdue_bills = Bill.objects.filter(user=user, due_date__lt=today, is_paid=False).filter(date_filter_overdue)
        recurring_bills = Bill.objects.filter(user=user).exclude(repeat_frequency=Bill.RepeatFrequency.DO_NOT_REPEAT)
        paid_bills = Bill.objects.filter(user=user, is_paid=True).filter(date_filter_paid)

        total_upcoming = upcoming_bills.aggregate(Sum('amount'))['amount__sum'] or 0
        total_overdue = overdue_bills.aggregate(Sum('amount'))['amount__sum'] or 0
        total_recurring = recurring_bills.aggregate(Sum('amount'))['amount__sum'] or 0
        total_paid = paid_bills.aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            "upcoming": BillSerializer(upcoming_bills, many=True).data,
            "overdue": BillSerializer(overdue_bills, many=True).data,
            "recurring": BillSerializer(recurring_bills, many=True).data,
            "paid": BillSerializer(paid_bills, many=True).data,
            "totalUpcoming": total_upcoming,
            "totalOverdue": total_overdue,
            "totalRecurring": total_recurring,
            "totalPaid": total_paid,
        })