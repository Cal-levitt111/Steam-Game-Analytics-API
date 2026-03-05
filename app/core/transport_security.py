from __future__ import annotations

from ipaddress import ip_address, ip_network

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, Response


def _normalize_forwarded_proto(header_value: str) -> str | None:
    candidate = header_value.split(',')[0].strip().lower()
    if candidate in {'http', 'https'}:
        return candidate
    return None


def _is_trusted_proxy(client_host: str | None, trusted_proxy_cidrs: tuple[str, ...]) -> bool:
    if not client_host or not trusted_proxy_cidrs:
        return False
    try:
        client_ip = ip_address(client_host)
    except ValueError:
        return False

    for cidr in trusted_proxy_cidrs:
        if client_ip in ip_network(cidr, strict=False):
            return True
    return False


def effective_request_scheme(request: Request, trusted_proxy_cidrs: tuple[str, ...]) -> str:
    client_host = request.client.host if request.client else None
    forwarded_proto = request.headers.get('x-forwarded-proto')
    if forwarded_proto and _is_trusted_proxy(client_host, trusted_proxy_cidrs):
        trusted_proto = _normalize_forwarded_proto(forwarded_proto)
        if trusted_proto is not None:
            return trusted_proto
    return request.url.scheme.lower()


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, force_https: bool, trusted_proxy_cidrs: tuple[str, ...]):
        super().__init__(app)
        self.force_https = force_https
        self.trusted_proxy_cidrs = trusted_proxy_cidrs

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.force_https and effective_request_scheme(request, self.trusted_proxy_cidrs) != 'https':
            https_url = request.url.replace(scheme='https')
            return RedirectResponse(url=str(https_url), status_code=307)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        trusted_proxy_cidrs: tuple[str, ...],
        hsts_max_age_seconds: int,
    ):
        super().__init__(app)
        self.trusted_proxy_cidrs = trusted_proxy_cidrs
        self.hsts_max_age_seconds = hsts_max_age_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        if self.hsts_max_age_seconds > 0 and effective_request_scheme(request, self.trusted_proxy_cidrs) == 'https':
            response.headers.setdefault(
                'Strict-Transport-Security',
                f'max-age={self.hsts_max_age_seconds}; includeSubDomains; preload',
            )
        return response
