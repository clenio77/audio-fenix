"""
Usage Limiter - Business Layer

Controla os limites de uso baseado no plano do usuário.
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional


class SubscriptionPlan(str, Enum):
    """Planos de assinatura disponíveis"""
    FREE = "free"
    PRO = "pro"


class UsageLimits:
    """Limites por plano"""
    
    FREE = {
        "max_file_size_mb": 20,
        "max_duration_minutes": 5,
        "max_uploads_per_day": 5,
        "export_quality": "mp3_192",
        "watermark": True,
        "retention_hours": 24,
    }
    
    PRO = {
        "max_file_size_mb": 100,
        "max_duration_minutes": 25,
        "max_uploads_per_day": None,  # Ilimitado
        "export_quality": "wav_44100",
        "watermark": False,
        "retention_hours": 720,  # 30 dias
    }


class UsageLimiter:
    """Verifica se o usuário pode realizar uma ação"""
    
    def __init__(self, user_plan: SubscriptionPlan):
        self.plan = user_plan
        self.limits = UsageLimits.PRO if user_plan == SubscriptionPlan.PRO else UsageLimits.FREE
    
    def can_upload(self, file_size_mb: float, duration_minutes: float) -> tuple[bool, Optional[str]]:
        """
        Verifica se o usuário pode fazer upload do arquivo.
        
        Returns:
            (can_upload, error_message)
        """
        # Verificar tamanho
        if file_size_mb > self.limits["max_file_size_mb"]:
            return False, f"Arquivo muito grande. Limite: {self.limits['max_file_size_mb']}MB"
        
        # Verificar duração
        if duration_minutes > self.limits["max_duration_minutes"]:
            return False, f"Áudio muito longo. Limite: {self.limits['max_duration_minutes']} minutos"
        
        return True, None
    
    def check_daily_quota(self, uploads_today: int) -> tuple[bool, Optional[str]]:
        """
        Verifica se o usuário ainda tem cota disponível hoje.
        
        Args:
            uploads_today: Número de uploads já realizados hoje
            
        Returns:
            (has_quota, error_message)
        """
        max_uploads = self.limits["max_uploads_per_day"]
        
        # Pro tem uploads ilimitados
        if max_uploads is None:
            return True, None
        
        if uploads_today >= max_uploads:
            return False, f"Limite diário atingido ({max_uploads} uploads). Upgrade para Pro!"
        
        return True, None
    
    def get_export_format(self) -> str:
        """Retorna o formato de exportação permitido"""
        return self.limits["export_quality"]
    
    def should_add_watermark(self) -> bool:
        """Verifica se deve adicionar marca d'água"""
        return self.limits["watermark"]
    
    def get_retention_hours(self) -> int:
        """Retorna o tempo de retenção dos arquivos"""
        return self.limits["retention_hours"]


def get_upgrade_message(current_plan: SubscriptionPlan) -> dict:
    """
    Retorna mensagem de upgrade para usuários Free.
    
    Returns:
        Dicionário com informações do plano Pro
    """
    if current_plan == SubscriptionPlan.PRO:
        return {}
    
    return {
        "message": "Upgrade para Pro e desbloqueie:",
        "benefits": [
            "✅ Uploads ilimitados",
            "✅ Arquivos até 100MB (≈25 minutos)",
            "✅ Qualidade WAV (44.1kHz)",
            "✅ Sem marca d'água",
            "✅ Histórico de 30 dias",
        ],
        "price": "$9.99/mês",
        "cta": "Fazer Upgrade",
    }
