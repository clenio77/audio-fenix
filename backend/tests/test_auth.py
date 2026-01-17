"""
Testes - Auth Service

Testa o serviço de autenticação.
"""
import pytest
from datetime import datetime
from domain.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from domain.models.user import User, UserPlan


class TestPasswordHashing:
    """Testes para hash de senha."""
    
    def test_hash_password(self):
        """Deve gerar hash de senha."""
        password = "senha123"
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Deve verificar senha correta."""
        password = "senha123"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Deve rejeitar senha incorreta."""
        password = "senha123"
        wrong_password = "senha456"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(wrong_password, hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Senhas diferentes devem ter hashes diferentes."""
        hash1 = AuthService.hash_password("senha1")
        hash2 = AuthService.hash_password("senha2")
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Mesma senha deve gerar hashes diferentes (salt)."""
        password = "mesma_senha"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        
        assert hash1 != hash2
        # Mas ambos devem validar
        assert AuthService.verify_password(password, hash1) is True
        assert AuthService.verify_password(password, hash2) is True


class TestJWTTokens:
    """Testes para tokens JWT."""
    
    def test_create_access_token(self):
        """Deve criar token de acesso."""
        token = AuthService.create_access_token(
            user_id="user-123",
            email="test@example.com",
            plan="free"
        )
        
        assert token is not None
        assert len(token) > 0
    
    def test_decode_access_token(self):
        """Deve decodificar token de acesso."""
        user_id = "user-123"
        email = "test@example.com"
        plan = "free"
        
        token = AuthService.create_access_token(user_id, email, plan)
        payload = AuthService.decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["plan"] == plan
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Deve criar token de refresh."""
        token = AuthService.create_refresh_token("user-123")
        
        assert token is not None
        assert len(token) > 0
    
    def test_decode_refresh_token(self):
        """Deve decodificar token de refresh."""
        user_id = "user-123"
        
        token = AuthService.create_refresh_token(user_id)
        payload = AuthService.decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_decode_invalid_token(self):
        """Deve retornar None para token inválido."""
        result = AuthService.decode_token("invalid-token")
        
        assert result is None
    
    def test_token_has_expiration(self):
        """Token deve ter expiração."""
        token = AuthService.create_access_token("user-123", "test@example.com", "free")
        payload = AuthService.decode_token(token)
        
        assert "exp" in payload
        assert "iat" in payload


class TestUserRegistration:
    """Testes para registro de usuário."""
    
    def test_register_user_success(self, db_session):
        """Deve registrar usuário com sucesso."""
        user, error = AuthService.register_user(
            db=db_session,
            email="novo@example.com",
            password="senha123",
            name="Novo Usuário"
        )
        
        assert error is None
        assert user is not None
        assert user.email == "novo@example.com"
        assert user.name == "Novo Usuário"
        assert user.plan == UserPlan.FREE.value
    
    def test_register_user_duplicate_email(self, db_session):
        """Não deve permitir email duplicado."""
        # Primeiro registro
        AuthService.register_user(
            db=db_session,
            email="duplicate@example.com",
            password="senha123"
        )
        
        # Segundo registro com mesmo email
        user, error = AuthService.register_user(
            db=db_session,
            email="duplicate@example.com",
            password="outrasenha"
        )
        
        assert user is None
        assert error == "Email já cadastrado"
    
    def test_register_user_invalid_email(self, db_session):
        """Não deve permitir email inválido."""
        user, error = AuthService.register_user(
            db=db_session,
            email="email-invalido",
            password="senha123"
        )
        
        assert user is None
        assert "inválido" in error.lower()
    
    def test_register_user_short_password(self, db_session):
        """Não deve permitir senha curta."""
        user, error = AuthService.register_user(
            db=db_session,
            email="test@example.com",
            password="12345"  # Menos de 6 caracteres
        )
        
        assert user is None
        assert "6 caracteres" in error
    
    def test_register_user_email_normalized(self, db_session):
        """Email deve ser normalizado (lowercase, trim)."""
        user, error = AuthService.register_user(
            db=db_session,
            email="  TEST@EXAMPLE.COM  ",
            password="senha123"
        )
        
        assert user is not None
        assert user.email == "test@example.com"


class TestUserAuthentication:
    """Testes para autenticação de usuário."""
    
    def test_authenticate_user_success(self, db_session):
        """Deve autenticar usuário válido."""
        # Registrar usuário
        AuthService.register_user(
            db=db_session,
            email="auth@example.com",
            password="senha123"
        )
        
        # Autenticar
        user = AuthService.authenticate_user(
            db=db_session,
            email="auth@example.com",
            password="senha123"
        )
        
        assert user is not None
        assert user.email == "auth@example.com"
    
    def test_authenticate_user_wrong_password(self, db_session):
        """Deve rejeitar senha incorreta."""
        AuthService.register_user(
            db=db_session,
            email="wrongpass@example.com",
            password="senhaCorreta"
        )
        
        user = AuthService.authenticate_user(
            db=db_session,
            email="wrongpass@example.com",
            password="senhaErrada"
        )
        
        assert user is None
    
    def test_authenticate_user_not_found(self, db_session):
        """Deve retornar None para usuário inexistente."""
        user = AuthService.authenticate_user(
            db=db_session,
            email="naoexiste@example.com",
            password="qualquersenha"
        )
        
        assert user is None
    
    def test_authenticate_updates_last_login(self, db_session):
        """Deve atualizar last_login após autenticação."""
        AuthService.register_user(
            db=db_session,
            email="lastlogin@example.com",
            password="senha123"
        )
        
        user = AuthService.authenticate_user(
            db=db_session,
            email="lastlogin@example.com",
            password="senha123"
        )
        
        assert user.last_login is not None


class TestChangePassword:
    """Testes para alteração de senha."""
    
    def test_change_password_success(self, db_session):
        """Deve alterar senha com sucesso."""
        user, _ = AuthService.register_user(
            db=db_session,
            email="changepass@example.com",
            password="senhaAntiga"
        )
        
        success, error = AuthService.change_password(
            db=db_session,
            user=user,
            current_password="senhaAntiga",
            new_password="senhaNova123"
        )
        
        assert success is True
        assert error is None
        
        # Verificar que nova senha funciona
        assert AuthService.verify_password("senhaNova123", user.hashed_password) is True
    
    def test_change_password_wrong_current(self, db_session):
        """Deve rejeitar se senha atual estiver errada."""
        user, _ = AuthService.register_user(
            db=db_session,
            email="wrongcurrent@example.com",
            password="senhaCorreta"
        )
        
        success, error = AuthService.change_password(
            db=db_session,
            user=user,
            current_password="senhaErrada",
            new_password="senhaNova123"
        )
        
        assert success is False
        assert "incorreta" in error.lower()
    
    def test_change_password_too_short(self, db_session):
        """Deve rejeitar nova senha curta."""
        user, _ = AuthService.register_user(
            db=db_session,
            email="shortpass@example.com",
            password="senha123"
        )
        
        success, error = AuthService.change_password(
            db=db_session,
            user=user,
            current_password="senha123",
            new_password="12345"
        )
        
        assert success is False
        assert "6 caracteres" in error
