from celery import shared_task
from django.core.mail import EmailMessage  # <--- Импортируем EmailMessage вместо send_mail
from django.conf import settings
from .models import Subscription


@shared_task
def send_course_update_email(course_id, course_title):
    subscriptions = Subscription.objects.filter(course_id=course_id).select_related('user')
    emails = [sub.user.email for sub in subscriptions if sub.user.email]

    if not emails:
        return f"Нет подписчиков у курса {course_title}"

    subject = f"Обновление материалов курса: {course_title}"
    message = f"Здравствуйте!\n\nВ курсе '{course_title}' появились новые материалы. Скорее заходите посмотреть!\n\nС уважением, команда платформы."

    # Используем EmailMessage для отправки со скрытой копией
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # От кого
        [],  # Кому (основные получатели)
        bcc=emails  # Скрытая копия (BCC)
    )
    email.send(fail_silently=False)

    return f"Письма отправлены {len(emails)} пользователям."