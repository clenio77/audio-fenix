"""
Testes - Business Layer: UsageLimiter

Testa a lógica de limitação de uso baseada no plano do usuário.
"""
import pytest
from business.usage_limiter import (
    UsageLimiter,
    SubscriptionPlan,
    UsageLimits,
    get_upgrade_message
)


class TestSubscriptionPlan:
    """Testes para o enum de planos de assinatura."""
    
    def test_free_plan_value(self):
        """Plano FREE deve ter valor 'free'."""
        assert SubscriptionPlan.FREE.value == "free"
    
    def test_pro_plan_value(self):
        """Plano PRO deve ter valor 'pro'."""
        assert SubscriptionPlan.PRO.value == "pro"
    
    def test_plan_is_string_enum(self):
        """Planos devem ser comparáveis como strings."""
        assert SubscriptionPlan.FREE == "free"
        assert SubscriptionPlan.PRO == "pro"


class TestUsageLimits:
    """Testes para os limites definidos por plano."""
    
    def test_free_limits_structure(self):
        """Limites FREE devem ter todas as chaves necessárias."""
        expected_keys = {
            "max_file_size_mb",
            "max_duration_minutes",
            "max_uploads_per_day",
            "export_quality",
            "watermark",
            "retention_hours",
        }
        assert set(UsageLimits.FREE.keys()) == expected_keys
    
    def test_pro_limits_structure(self):
        """Limites PRO devem ter todas as chaves necessárias."""
        expected_keys = {
            "max_file_size_mb",
            "max_duration_minutes",
            "max_uploads_per_day",
            "export_quality",
            "watermark",
            "retention_hours",
        }
        assert set(UsageLimits.PRO.keys()) == expected_keys
    
    def test_free_file_size_limit(self):
        """Limite de arquivo FREE deve ser 20MB."""
        assert UsageLimits.FREE["max_file_size_mb"] == 20
    
    def test_pro_file_size_limit(self):
        """Limite de arquivo PRO deve ser 100MB."""
        assert UsageLimits.PRO["max_file_size_mb"] == 100
    
    def test_free_has_watermark(self):
        """Plano FREE deve ter marca d'água."""
        assert UsageLimits.FREE["watermark"] is True
    
    def test_pro_no_watermark(self):
        """Plano PRO não deve ter marca d'água."""
        assert UsageLimits.PRO["watermark"] is False
    
    def test_free_daily_limit(self):
        """Plano FREE deve ter limite de 5 uploads diários."""
        assert UsageLimits.FREE["max_uploads_per_day"] == 5
    
    def test_pro_unlimited_uploads(self):
        """Plano PRO deve ter uploads ilimitados (None)."""
        assert UsageLimits.PRO["max_uploads_per_day"] is None


class TestUsageLimiterInit:
    """Testes de inicialização do UsageLimiter."""
    
    def test_free_plan_initialization(self):
        """Inicialização com plano FREE deve usar limites FREE."""
        limiter = UsageLimiter(SubscriptionPlan.FREE)
        assert limiter.plan == SubscriptionPlan.FREE
        assert limiter.limits == UsageLimits.FREE
    
    def test_pro_plan_initialization(self):
        """Inicialização com plano PRO deve usar limites PRO."""
        limiter = UsageLimiter(SubscriptionPlan.PRO)
        assert limiter.plan == SubscriptionPlan.PRO
        assert limiter.limits == UsageLimits.PRO


class TestCanUpload:
    """Testes para o método can_upload()."""
    
    @pytest.fixture
    def free_limiter(self):
        return UsageLimiter(SubscriptionPlan.FREE)
    
    @pytest.fixture
    def pro_limiter(self):
        return UsageLimiter(SubscriptionPlan.PRO)
    
    # === Testes de tamanho de arquivo ===
    
    def test_free_small_file_allowed(self, free_limiter):
        """Arquivo pequeno deve ser permitido no plano FREE."""
        can_upload, error = free_limiter.can_upload(file_size_mb=10, duration_minutes=3)
        assert can_upload is True
        assert error is None
    
    def test_free_large_file_rejected(self, free_limiter):
        """Arquivo maior que 20MB deve ser rejeitado no plano FREE."""
        can_upload, error = free_limiter.can_upload(file_size_mb=25, duration_minutes=3)
        assert can_upload is False
        assert "20MB" in error
    
    def test_pro_large_file_allowed(self, pro_limiter):
        """Arquivo de 50MB deve ser permitido no plano PRO."""
        can_upload, error = pro_limiter.can_upload(file_size_mb=50, duration_minutes=10)
        assert can_upload is True
        assert error is None
    
    def test_pro_very_large_file_rejected(self, pro_limiter):
        """Arquivo maior que 100MB deve ser rejeitado no plano PRO."""
        can_upload, error = pro_limiter.can_upload(file_size_mb=150, duration_minutes=10)
        assert can_upload is False
        assert "100MB" in error
    
    # === Testes de duração ===
    
    def test_free_short_audio_allowed(self, free_limiter):
        """Áudio curto deve ser permitido no plano FREE."""
        can_upload, error = free_limiter.can_upload(file_size_mb=5, duration_minutes=3)
        assert can_upload is True
        assert error is None
    
    def test_free_long_audio_rejected(self, free_limiter):
        """Áudio maior que 5 minutos deve ser rejeitado no plano FREE."""
        can_upload, error = free_limiter.can_upload(file_size_mb=5, duration_minutes=8)
        assert can_upload is False
        assert "5 minutos" in error
    
    def test_pro_long_audio_allowed(self, pro_limiter):
        """Áudio de 20 minutos deve ser permitido no plano PRO."""
        can_upload, error = pro_limiter.can_upload(file_size_mb=50, duration_minutes=20)
        assert can_upload is True
        assert error is None
    
    def test_pro_very_long_audio_rejected(self, pro_limiter):
        """Áudio maior que 25 minutos deve ser rejeitado no plano PRO."""
        can_upload, error = pro_limiter.can_upload(file_size_mb=50, duration_minutes=30)
        assert can_upload is False
        assert "25 minutos" in error
    
    # === Testes de limites exatos ===
    
    def test_free_exact_size_limit(self, free_limiter):
        """Arquivo exatamente no limite de tamanho deve ser permitido."""
        can_upload, error = free_limiter.can_upload(file_size_mb=20, duration_minutes=3)
        assert can_upload is True
    
    def test_free_exact_duration_limit(self, free_limiter):
        """Áudio exatamente no limite de duração deve ser permitido."""
        can_upload, error = free_limiter.can_upload(file_size_mb=10, duration_minutes=5)
        assert can_upload is True


class TestCheckDailyQuota:
    """Testes para o método check_daily_quota()."""
    
    @pytest.fixture
    def free_limiter(self):
        return UsageLimiter(SubscriptionPlan.FREE)
    
    @pytest.fixture
    def pro_limiter(self):
        return UsageLimiter(SubscriptionPlan.PRO)
    
    def test_free_first_upload_allowed(self, free_limiter):
        """Primeiro upload do dia deve ser permitido."""
        has_quota, error = free_limiter.check_daily_quota(uploads_today=0)
        assert has_quota is True
        assert error is None
    
    def test_free_fourth_upload_allowed(self, free_limiter):
        """Quarto upload do dia deve ser permitido (limite é 5)."""
        has_quota, error = free_limiter.check_daily_quota(uploads_today=4)
        assert has_quota is True
        assert error is None
    
    def test_free_fifth_upload_rejected(self, free_limiter):
        """Sexto upload do dia deve ser rejeitado (limite é 5)."""
        has_quota, error = free_limiter.check_daily_quota(uploads_today=5)
        assert has_quota is False
        assert "Limite diário" in error
    
    def test_pro_unlimited_uploads(self, pro_limiter):
        """Plano PRO deve permitir uploads ilimitados."""
        has_quota, error = pro_limiter.check_daily_quota(uploads_today=100)
        assert has_quota is True
        assert error is None


class TestExportFormat:
    """Testes para o método get_export_format()."""
    
    def test_free_export_format(self):
        """Plano FREE deve exportar em MP3 192kbps."""
        limiter = UsageLimiter(SubscriptionPlan.FREE)
        assert limiter.get_export_format() == "mp3_192"
    
    def test_pro_export_format(self):
        """Plano PRO deve exportar em WAV 44.1kHz."""
        limiter = UsageLimiter(SubscriptionPlan.PRO)
        assert limiter.get_export_format() == "wav_44100"


class TestWatermark:
    """Testes para o método should_add_watermark()."""
    
    def test_free_has_watermark(self):
        """Plano FREE deve adicionar marca d'água."""
        limiter = UsageLimiter(SubscriptionPlan.FREE)
        assert limiter.should_add_watermark() is True
    
    def test_pro_no_watermark(self):
        """Plano PRO não deve adicionar marca d'água."""
        limiter = UsageLimiter(SubscriptionPlan.PRO)
        assert limiter.should_add_watermark() is False


class TestRetentionHours:
    """Testes para o método get_retention_hours()."""
    
    def test_free_retention(self):
        """Plano FREE deve ter retenção de 24 horas."""
        limiter = UsageLimiter(SubscriptionPlan.FREE)
        assert limiter.get_retention_hours() == 24
    
    def test_pro_retention(self):
        """Plano PRO deve ter retenção de 30 dias (720 horas)."""
        limiter = UsageLimiter(SubscriptionPlan.PRO)
        assert limiter.get_retention_hours() == 720


class TestUpgradeMessage:
    """Testes para a função get_upgrade_message()."""
    
    def test_free_user_gets_upgrade_message(self):
        """Usuário FREE deve receber mensagem de upgrade."""
        message = get_upgrade_message(SubscriptionPlan.FREE)
        assert "message" in message
        assert "benefits" in message
        assert "price" in message
        assert len(message["benefits"]) > 0
    
    def test_pro_user_gets_empty_message(self):
        """Usuário PRO não deve receber mensagem de upgrade."""
        message = get_upgrade_message(SubscriptionPlan.PRO)
        assert message == {}
