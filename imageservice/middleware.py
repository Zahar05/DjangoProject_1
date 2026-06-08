import time
import logging

from .metrics import HTTP_REQUESTS_TOTAL

logger = logging.getLogger("imageservice")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        endpoint = (
            request.resolver_match.view_name
            if request.resolver_match
            else request.path
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()

        user = (
            request.user
            if request.user.is_authenticated
            else "Anonymous"
        )

        ip = self.get_client_ip(request)

        logger.info(
            f"{request.method} {request.path} | "
            f"user={user} | ip={ip} | "
            f"time={duration:.3f}s | status={response.status_code}"
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip