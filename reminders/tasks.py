from datetime import datetime
from django.utils.timezone import now
from celery import shared_task
from .models import Reminder

@shared_task
def check_due_reminders() -> int:
    n = 0
    qs = Reminder.objects.filter(delivered=False, due_at__lte=now()).order_by("due_at")
    for r in qs:
        # Hook up real notification here (email, SMS, push). For now, mark delivered.
        r.delivered = True
        r.save(update_fields=["delivered"])
        n += 1
    return n
