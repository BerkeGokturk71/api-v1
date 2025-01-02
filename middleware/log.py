from fastapi import FastAPI, Request
from datetime import datetime
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Logger'ı yapılandırma
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # İstemcinin IP adresini almak
        client_ip = request.client.host
        request_path = request.url.path
        # IP adresini loglamak
        logger.info(f"Incoming request from IP: {client_ip}")

        # IP'yi dosyaya kaydetme
        with open("ip_logs.txt", "a",encoding="utf-8") as log_file:
            log_file.write(f"{datetime.now()} - IP: {client_ip} - Path: {request_path}\n")

        # İsteği işleme devam et
        response = await call_next(request)
        return response
