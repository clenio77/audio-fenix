"""
Celery Worker - Model Layer

Configuração do Celery para processamento assíncrono de áudio.
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Configurar Celery
celery_app = Celery(
    "isomix",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutos
    task_soft_time_limit=540,  # 9 minutos
    worker_prefetch_multiplier=1,  # Processar 1 tarefa por vez
    worker_max_tasks_per_child=10,  # Reiniciar worker a cada 10 tarefas
)

# Auto-descobrir tarefas
celery_app.autodiscover_tasks(["model"])
