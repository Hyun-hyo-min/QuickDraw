from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import websockets
import asyncio
import logging
from app.config import settings

router = APIRouter()

SERVICE_URLS = {
    "draw": settings.DRAW_SERVICE_URL
}

logger = logging.getLogger(__name__)


@router.websocket("/ws/{service}/{path:path}")
async def proxy_websocket(service: str, path: str, websocket: WebSocket):
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        await websocket.close(code=1008)
        logger.warning(f"Invalid service: {service}")
        return

    service_ws_url = service_url.replace("http", "ws") + f"/{path}"

    try:
        async with websockets.connect(service_ws_url) as service_ws:
            await websocket.accept()
            logger.info(f"WebSocket connection established with {service_ws_url}")

            async def forward_to_service():
                try:
                    async for message in websocket.iter_text():
                        await service_ws.send(message)
                except WebSocketDisconnect:
                    logger.info("Client WebSocket disconnected")
                    await service_ws.close()

            async def forward_to_client():
                try:
                    async for message in service_ws:
                        await websocket.send_text(message)
                except websockets.ConnectionClosed:
                    logger.info("Service WebSocket disconnected")
                    await websocket.close()

            await asyncio.gather(forward_to_service(), forward_to_client())

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except websockets.ConnectionClosed:
        logger.info("WebSocket disconnected by service")
    except Exception as e:
        logger.error(f"WebSocket Proxy Error: {e}", exc_info=True)
        await websocket.close(code=1011)
    finally:
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error while closing WebSocket: {e}", exc_info=True)
