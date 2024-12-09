import httpx
import websockets
import asyncio
import logging
from fastapi import APIRouter, WebSocket, Request, Response, WebSocketDisconnect, HTTPException, WebSocketState
from app.config import settings

router = APIRouter()

SERVICE_URLS = {
    "user": settings.USER_SERVICE_URL,
    "room": settings.ROOM_SERVICE_URL,
    "draw": settings.DRAW_SERVICE_URL
}

logger = logging.getLogger(__name__)


@router.api_route("/api/v1/{service}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(request: Request, service: str, path: str = ""):
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        logger.error(f"Service {service} not found in SERVICE_URLS.")
        raise HTTPException(status_code=404, detail="Service not found")

    query_params = dict(request.query_params)
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    logger.info(f"Proxying request to {service}:")
    logger.info(f"URL: {service_url}/{service}/{path}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Query params: {query_params}")
    logger.info(f"Body: {body.decode('utf-8') if body else None}")

    try:
        async with httpx.AsyncClient(timeout=settings.TIME_OUT) as client:
            response = await client.request(
                method=request.method,
                url=f"{service_url}/{path}" if path else service_url,
                headers=headers,
                params=query_params,
                content=body,
            )
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text}")

        if response.headers.get("content-type") == "application/json":
            return response.json()
        else:
            return Response(content=response.content, media_type=response.headers.get("content-type"))

    except httpx.RequestError as exc:
        logger.error(f"HTTP request to {service_url} failed: {exc}")
        raise HTTPException(
            status_code=500, detail=f"Error connecting to service: {service}"
        ) from exc


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
            logger.info(f"WebSocket connection established with {
                        service_ws_url}")

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
                except WebSocketDisconnect:
                    logger.info("Service WebSocket disconnected")
                    await websocket.close()

            await asyncio.gather(forward_to_service(), forward_to_client())

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client or service")
    except Exception as e:
        logger.error(f"WebSocket Proxy Error: {e}", exc_info=True)
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=1011)
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            logger.info("Closing WebSocket connection")
            await websocket.close()
