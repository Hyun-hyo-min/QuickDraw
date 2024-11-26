import httpx
import websockets
import asyncio
from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect, HTTPException
from app.config import settings

router = APIRouter()

SERVICE_URLS = {
    "user": settings.USER_SERVICE_URL,
    "room": settings.ROOM_SERVICE_URL,
    "draw": settings.DRAW_SERVICE_URL
}


# HTTP 요청 프록시
@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service: str, path: str, request: Request):
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        raise HTTPException(status_code=404, detail="Service not found")

    query_params = dict(request.query_params)
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=settings.TIME_OUT) as client:
            response = await client.request(
                method=request.method,
                url=f"{service_url}/{path}",
                headers=headers,
                params=query_params,
                content=body,
            )
        return response.json() if response.headers.get("content-type") == "application/json" else response.text

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to service: {service}"
        ) from exc


@router.websocket("/{service}/{path:path}")
async def proxy_websocket(service: str, path: str, websocket: WebSocket):
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        await websocket.close(code=1008)  # Policy Violation
        return

    service_ws_url = service_url.replace("http", "ws") + f"/{path}"

    try:
        # WebSocket 서비스에 연결
        async with websockets.connect(service_ws_url) as service_ws:
            await websocket.accept()

            async def forward_to_service():
                async for message in websocket.iter_text():
                    await service_ws.send(message)

            async def forward_to_client():
                async for message in service_ws:
                    await websocket.send_text(message)

            await asyncio.gather(forward_to_service(), forward_to_client())

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.close(code=1011)  # Internal Error
        print(f"WebSocket Proxy Error: {e}")


