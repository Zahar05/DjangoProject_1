from prometheus_client import Counter, Histogram


IMAGES_UPLOADED = Counter(
    "images_uploaded_total",
    "Total uploaded images"
)

IMAGES_DOWNLOADED = Counter(
    "images_downloaded_total",
    "Total downloaded images"
)

IMAGES_DELETED = Counter(
    "images_deleted_total",
    "Total deleted images"
)

USERS_REGISTERED = Counter(
    "users_registered_total",
    "Total registered users"
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION_SECONDS = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)