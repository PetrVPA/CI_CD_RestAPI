from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Payment
from .services import get_stripe_payment_status
from study.models import Subscription
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model() # Получаем модель пользователя (у вас это Student)

@shared_task
def check_pending_payments():
    """
    Периодическая задача: проверяет неоплаченные платежи в Stripe.
    """
    logger.info("Запуск проверки неоплаченных платежей...")
    pending_payments = Payment.objects.filter(is_paid=False, stripe_session_id__isnull=False)

    for payment in pending_payments:
        status = get_stripe_payment_status(payment.stripe_session_id)

        if status == 'paid':
            payment.is_paid = True
            payment.save()

            # Если это оплата за курс, создаем подписку
            if payment.study_course:
                Subscription.objects.get_or_create(
                    user=payment.user,
                    course=payment.study_course
                )
            logger.info(f"Платеж {payment.id} успешно подтвержден.")

    return f"Проверено платежей: {pending_payments.count()}"


@shared_task
def deactivate_inactive_users():
    """
    Проверяет пользователей и блокирует (is_active=False) тех,
    кто не заходил более 30 дней.
    """
    # Вычисляем дату, которая была 30 дней назад от текущего момента
    one_month_ago = timezone.now() - timedelta(days=30)

    # Ищем активных пользователей, у которых last_login меньше этой даты
    # ВАЖНО: Если пользователь ни разу не входил, last_login будет None.
    # Мы ищем тех, кто входил (last_login__isnull=False), но давно.
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago,
        last_login__isnull=False
    )

    # Считаем, сколько нашли
    count = inactive_users.count()

    if count > 0:
        # Обновляем флаг is_active на False для всех найденных сразу
        # Это делает один SQL-запрос, что намного быстрее, чем цикл for
        updated_count = inactive_users.update(is_active=False)
        logger.info(f"Заблокировано {updated_count} неактивных пользователей.")
        return f"Заблокировано {updated_count} пользователей."

    logger.info("Неактивных пользователей не найдено.")
    return "Неактивных пользователей не найдено."
