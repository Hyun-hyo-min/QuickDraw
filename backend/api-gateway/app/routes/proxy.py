import httpx
from fastapi import APIRouter, Request, HTTPException
from app.config import settings

router = APIRouter()

# 서비스 URL 설정
SERVICE_URLS = {
    "user": settings.USER_SERVICE_URL,
    "room": settings.ROOM_SERVICE_URL,
    "draw": settings.DRAW_SERVICE_URL
}

# HTTP 요청 타임아웃 설정 (초 단위)
TIMEOUT = 10.0

@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service: str, path: str, request: Request):
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        raise HTTPException(status_code=404, detail="Service not found")

    # 쿼리 파라미터 전달
    query_params = dict(request.query_params)

    # 요청 헤더 준비
    headers = dict(request.headers)
    headers.pop("host", None)  # Host 헤더 제거 (httpx가 자동 처리)

    # 요청 바디 준비
    body = await request.body()

    try:
        # HTTP 클라이언트 요청
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=f"{service_url}/{path}",
                headers=headers,
                params=query_params,
                content=body,
            )

        # 응답 반환
        return response.json() if response.headers.get("content-type") == "application/json" else response.text

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to service: {service}"
        ) from exc
