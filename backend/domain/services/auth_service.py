"""
Auth Service - Domain Layer

Serviço de autenticação com JWT.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os

from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from domain.models.user import User, UserPlan


# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-isomix-studio-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class AuthService:
    """Serviço de autenticação e autorização."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash da senha usando bcrypt.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        # Truncar senha para 72 bytes (limite do bcrypt)
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha está correta.
        
        Args:
            plain_password: Senha em texto plano
            hashed_password: Hash da senha armazenada
            
        Returns:
            True se a senha está correta
        """
        password_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @staticmethod
    def create_access_token(user_id: str, email: str, plan: str) -> str:
        """
        Cria um token JWT de acesso.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            plan: Plano do usuário
            
        Returns:
            Token JWT
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "email": email,
            "plan": plan,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Cria um token JWT de refresh.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Token JWT de refresh
        """
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decodifica e valida um token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Payload do token ou None se inválido
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica um usuário por email e senha.
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            password: Senha em texto plano
            
        Returns:
            User se autenticado, None caso contrário
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        name: Optional[str] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Registra um novo usuário.
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            password: Senha em texto plano
            name: Nome do usuário (opcional)
            
        Returns:
            Tupla (User, None) se sucesso, (None, error_message) se erro
        """
        # Verificar se email já existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None, "Email já cadastrado"
        
        # Validar email
        if not email or "@" not in email:
            return None, "Email inválido"
        
        # Validar senha
        if len(password) < 6:
            return None, "Senha deve ter pelo menos 6 caracteres"
        
        # Criar usuário
        user = User(
            email=email.lower().strip(),
            hashed_password=AuthService.hash_password(password),
            name=name,
            plan=UserPlan.FREE.value,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user, None
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Busca usuário por ID.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            User ou None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Altera a senha do usuário.
        
        Args:
            db: Sessão do banco de dados
            user: Usuário
            current_password: Senha atual
            new_password: Nova senha
            
        Returns:
            Tupla (success, error_message)
        """
        if not AuthService.verify_password(current_password, user.hashed_password):
            return False, "Senha atual incorreta"
        
        if len(new_password) < 6:
            return False, "Nova senha deve ter pelo menos 6 caracteres"
        
        user.hashed_password = AuthService.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return True, None
