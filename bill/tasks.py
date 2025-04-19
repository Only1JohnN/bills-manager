from celery import shared_task
from .models import Bill
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import timedelta

@shared_task
def recreate_bills(bill_id):
    """Recreate bills for the given bill ID."""
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)

    logger.info(f"Task recreate_bills called with bill_id: {bill_id}")

    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        logger.error(f"Bill with ID {bill_id} does not exist.")
        return  # Exit if the bill does not exist

    today = now().date()
    end_date = today.replace(year=today.year + 1)  # Generate up to 1 year from now
    next_due_date = bill.due_date

    logger.info(f"Starting to create recurring bills for bill ID {bill_id} from {next_due_date} to {end_date}")

    while next_due_date <= end_date:
        # Skip if a bill with the same user and due_date already exists
        if Bill.objects.filter(user=bill.user, bill_name=bill.bill_name, due_date=next_due_date).exists():
            logger.warning(f"Bill for {next_due_date} already exists. Skipping.")
            next_due_date = calculate_next_due_date(bill, next_due_date)
            continue

        # Create a new bill instance for the next occurrence
        new_bill = Bill.objects.create(
            user=bill.user,
            bill_name=bill.bill_name,
            amount=bill.amount,
            category=bill.category,
            service_provider=bill.service_provider,
            due_date=next_due_date,
            next_due_date=next_due_date,
            repeat_frequency=bill.repeat_frequency,
            reminder=bill.reminder,
            priority=bill.priority,
            auto_pay=bill.auto_pay,
            attach_photo=bill.attach_photo,
            notes=bill.notes,
        )

        logger.info(f"Created new bill with ID {new_bill.id} for due date {next_due_date}")

        # Calculate the next due date
        next_due_date = calculate_next_due_date(bill, bill.due_date)


    logger.info(f"Finished creating recurring bills for bill ID {bill_id}")


def calculate_next_due_date(bill, current_due_date):
    """Calculate the next due date based on repeat_frequency."""
    if bill.repeat_frequency == Bill.RepeatFrequency.DAILY:
        return current_due_date + timedelta(days=1)
    elif bill.repeat_frequency == Bill.RepeatFrequency.WEEKLY:
        return current_due_date + timedelta(weeks=1)
    elif bill.repeat_frequency == Bill.RepeatFrequency.BI_WEEKLY:
        return current_due_date + timedelta(weeks=2)
    elif bill.repeat_frequency == Bill.RepeatFrequency.MONTHLY:
        return current_due_date + relativedelta(months=1)
    elif bill.repeat_frequency == Bill.RepeatFrequency.BI_MONTHLY:
        return current_due_date + relativedelta(months=2)
    elif bill.repeat_frequency == Bill.RepeatFrequency.ANNUALLY:
        return current_due_date + relativedelta(years=1)
    return None  # For DO_NOT_REPEAT or CUSTOM