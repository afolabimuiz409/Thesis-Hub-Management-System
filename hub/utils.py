from .models import Notification


def create_notification(
    recipient,
    title,
    message,
    topic=None
):
   return Notification.objects.create(
    recipient=recipient,
    title=title,
    message=message,
    topic=topic,
   )