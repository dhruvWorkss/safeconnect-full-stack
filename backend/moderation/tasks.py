from celery import shared_task
from django.contrib.auth import get_user_model
from .models import ModerationCase, Notification
@shared_task
def notify_critical_case(case_id):
    case=ModerationCase.objects.get(pk=case_id)
    moderators=get_user_model().objects.filter(organization=case.report.organization,role__in=["moderator","admin"])
    Notification.objects.bulk_create([Notification(organization=case.report.organization,user=user,message=f"Critical case {case.report.public_id} requires review.") for user in moderators])
    return moderators.count()
