from django.conf import settings
from django.db import models
from django.utils import timezone

class Bill(models.Model):
    class RepeatFrequency(models.TextChoices):
        DO_NOT_REPEAT = 'do_not_repeat', 'Do not repeat'
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        BI_WEEKLY = 'bi_weekly', 'Bi-weekly'
        MONTHLY = 'monthly', 'Monthly'
        BI_MONTHLY = 'bi_monthly', 'Bi-monthly'
        ANNUALLY = 'annually', 'Annually'
        CUSTOM = 'custom', 'Custom'

    class ReminderChoices(models.TextChoices):
        NO_REMINDER = 'no_reminder', 'No Reminder'
        SAME_DAY = 'same_day', 'Remind on same day'
        ONE_DAY_BEFORE = '1_day_before', 'Remind 1 Day Before'
        TWO_DAYS_BEFORE = '2_days_before', 'Remind 2 Days Before'
        THREE_DAYS_BEFORE = '3_days_before', 'Remind 3 Days Before'
        FOUR_DAYS_BEFORE = '4_days_before', 'Remind 4 Days Before'
        FIVE_DAYS_BEFORE = '5_days_before', 'Remind 5 Days Before'
        TEN_DAYS_BEFORE = '10_days_before', 'Remind 10 Days Before'
        FIFTEEN_DAYS_BEFORE = '15_days_before', 'Remind 15 Days Before'
        TWENTY_DAYS_BEFORE = '20_days_before', 'Remind 20 Days Before'
        THIRTY_DAYS_BEFORE = '30_days_before', 'Remind 30 Days Before'

    class PriorityChoices(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bills')
    bill_name = models.CharField(max_length=100, blank=True)  # Optional field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)  # Required by default
    service_provider = models.CharField(max_length=100)  # Required by default
    due_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    repeat_frequency = models.CharField(
        max_length=50,
        choices=RepeatFrequency.choices,
        default=RepeatFrequency.DO_NOT_REPEAT
    )
    reminder = models.CharField(
        max_length=50,
        choices=ReminderChoices.choices,
        default=ReminderChoices.NO_REMINDER
    )
    priority = models.CharField(
        max_length=50,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
    )
    auto_pay = models.BooleanField(default=False)
    attach_photo = models.ImageField(upload_to='bill_photos/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.bill_name and self.service_provider:
            self.bill_name = self.service_provider

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.repeat_frequency != self.RepeatFrequency.DO_NOT_REPEAT:
            from .tasks import recreate_bills  # Lazy import
            recreate_bills.delay(self.id)

    def __str__(self):
        return f"{self.bill_name or self.service_provider} - {self.user.username}"
    
    
    @property
    def status(self):
        if self.payment_date:
            return 'paid'
        elif self.due_date and self.due_date < timezone.now().date():
            return 'overdue'
        elif self.due_date and self.due_date >= timezone.now().date():
            return 'upcoming'
        elif self.repeat_frequency:
            return 'recurring'
        return None