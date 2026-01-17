"""
WebSocket Manager - Application Layer

Gerenciador de conexões WebSocket para atualizações em tempo real.
"""
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    """
    Gerencia conexões WebSocket para notificações em tempo real.
    
    Suporta:
    - Conexões por projeto (para status de processamento)
    - Broadcast para todos os conectados
    - Mensagens tipadas com JSON
    """
    
    def __init__(self):
        # Conexões por projeto_id
        self.project_connections: Dict[str, Set[WebSocket]] = {}
        # Todas as conexões ativas
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, project_id: Optional[str] = None):
        """
        Aceita nova conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
            project_id: ID do projeto para inscrição (opcional)
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if project_id:
            if project_id not in self.project_connections:
                self.project_connections[project_id] = set()
            self.project_connections[project_id].add(websocket)
            
            # Enviar confirmação de conexão
            await self.send_personal(websocket, {
                "type": "connected",
                "project_id": project_id,
                "message": "Conectado ao projeto"
            })
    
    def disconnect(self, websocket: WebSocket, project_id: Optional[str] = None):
        """
        Remove conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
            project_id: ID do projeto (opcional)
        """
        self.active_connections.discard(websocket)
        
        if project_id and project_id in self.project_connections:
            self.project_connections[project_id].discard(websocket)
            
            # Limpar set vazio
            if not self.project_connections[project_id]:
                del self.project_connections[project_id]
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """
        Envia mensagem para uma conexão específica.
        
        Args:
            websocket: Conexão WebSocket
            message: Mensagem como dicionário
        """
        try:
            await websocket.send_json(message)
        except Exception:
            # Conexão pode ter sido fechada
            pass
    
    async def send_to_project(self, project_id: str, message: dict):
        """
        Envia mensagem para todos os conectados a um projeto.
        
        Args:
            project_id: ID do projeto
            message: Mensagem como dicionário
        """
        if project_id not in self.project_connections:
            return
        
        # Coletar conexões mortas para remoção
        dead_connections = []
        
        for websocket in self.project_connections[project_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.append(websocket)
        
        # Remover conexões mortas
        for ws in dead_connections:
            self.project_connections[project_id].discard(ws)
            self.active_connections.discard(ws)
    
    async def broadcast(self, message: dict):
        """
        Envia mensagem para TODAS as conexões ativas.
        
        Args:
            message: Mensagem como dicionário
        """
        dead_connections = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.append(websocket)
        
        # Remover conexões mortas
        for ws in dead_connections:
            self.active_connections.discard(ws)
    
    async def notify_project_status(
        self,
        project_id: str,
        status: str,
        progress: int = 0,
        message: str = "",
        error: Optional[str] = None
    ):
        """
        Notifica status de processamento de um projeto.
        
        Args:
            project_id: ID do projeto
            status: Status atual (pending, processing, ready, failed)
            progress: Porcentagem de progresso (0-100)
            message: Mensagem descritiva
            error: Mensagem de erro (se aplicável)
        """
        await self.send_to_project(project_id, {
            "type": "project_status",
            "project_id": project_id,
            "status": status,
            "progress": progress,
            "message": message,
            "error": error,
        })
    
    def get_connection_count(self, project_id: Optional[str] = None) -> int:
        """
        Retorna número de conexões ativas.
        
        Args:
            project_id: ID do projeto (opcional, para contagem específica)
            
        Returns:
            Número de conexões
        """
        if project_id:
            return len(self.project_connections.get(project_id, set()))
        return len(self.active_connections)


# Instância global do gerenciador
manager = ConnectionManager()
