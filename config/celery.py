#from config import celery
import os
from celery import Celery
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Устанавливаем дефолтные настройки Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # Замените 'config' на имя вашей папки с settings.py

app = Celery('myproject') # Замените 'myproject' на имя вашего проекта

# Используем настройки Django с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем задачи (tasks.py) в ваших приложениях
app.autodiscover_tasks()