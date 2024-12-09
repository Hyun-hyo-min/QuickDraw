from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import logging
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
