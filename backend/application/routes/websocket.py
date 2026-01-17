"""
WebSocket Routes - Application Layer

Endpoints WebSocket para comunicação em tempo real.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from application.websocket import manager

router = APIRouter()


@router.websocket("/ws/project/{project_id}")
async def websocket_project(
    websocket: WebSocket,
    project_id: str
):
    """
    WebSocket para acompanhar status de um projeto específico.
    
    Eventos enviados:
    - connected: Confirmação de conexão
    - project_status: Atualização de status do projeto
    - processing_progress: Progresso do processamento
    - stems_ready: Stems prontos para uso
    - error: Erro no processamento
    
    Exemplo de uso (JavaScript):
    ```js
    const ws = new WebSocket('ws://localhost:8000/ws/project/abc123');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.type, data);
    };
    ```
    """
    await manager.connect(websocket, project_id)
    
    try:
        while True:
            # Aguardar mensagens do cliente (keep-alive ou comandos)
            data = await websocket.receive_json()
            
            # Responder a pings
            if data.get("type") == "ping":
                await manager.send_personal(websocket, {
                    "type": "pong",
                    "project_id": project_id
                })
            
            # Solicitar status atual
            elif data.get("type") == "get_status":
                # Aqui poderia buscar status do banco e enviar
                await manager.send_personal(websocket, {
                    "type": "status_requested",
                    "project_id": project_id,
                    "message": "Status será enviado automaticamente"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
    except Exception as e:
        manager.disconnect(websocket, project_id)


@router.websocket("/ws/global")
async def websocket_global(websocket: WebSocket):
    """
    WebSocket global para notificações do sistema.
    
    Recebe broadcasts de:
    - Novos projetos
    - Atualizações de sistema
    - Métricas de uso
    """
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await manager.send_personal(websocket, {"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
