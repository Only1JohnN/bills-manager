from rest_framework import serializers
from .models import Bill
from datetime import date
from .tasks import recreate_bills


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'id',
            'bill_name',
            'amount',
            'category',
            'service_provider',
            'due_date', 
            'next_due_date',
            'repeat_frequency',
            'reminder',
            'priority',
            'auto_pay',
            'attach_photo',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id','created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user

        if not validated_data.get('bill_name'):
            validated_data['bill_name'] = validated_data.get('service_provider', 'Unnamed Bill')

        bill = super().create(validated_data)

        if bill.repeat_frequency != Bill.RepeatFrequency.DO_NOT_REPEAT:
            print(f"Triggering recreate_bills task for bill {bill.id}")
            recreate_bills.delay(bill.id)  # Pass the new bill's ID

        return bill
