import psycopg2
import redis
import time
import os
import json
import uuid
import logging

from flask import Flask, Response, request, g
from prometheus_client import Counter, generate_latest
from werkzeug.exceptions import HTTPException

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


time.sleep(20)

SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")
APP_ENV = os.getenv("APP_ENV", "dev")
POD_NAME = os.getenv("HOSTNAME", "unknown")
LOG_PROBES = os.getenv("LOG_PROBES", "false").lower() == "true"

OTEL_ENABLED = os.getenv("OTEL_ENABLED", "false").lower() == "true"
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://otel-collector.tracing.svc.cluster.local:4317"
)


def setup_tracing():
    if not OTEL_ENABLED:
        return

    resource = Resource.create({
        "service.name": SERVICE_NAME,
        "service.namespace": "devops-platform",
        "deployment.environment": APP_ENV,
        "k8s.pod.name": POD_NAME,
    })

    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )

    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)


app = Flask(__name__)

setup_tracing()

if OTEL_ENABLED:
    FlaskInstrumentor().instrument_app(
        app,
        excluded_urls="/health,/metrics",
    )

# Disable default Flask/Werkzeug access logs.
# We emit structured JSON logs ourselves.
logging.getLogger("werkzeug").disabled = True


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)


def log_json(level, event, **fields):
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "service": SERVICE_NAME,
        "env": APP_ENV,
        "pod": POD_NAME,
        "event": event,
        **fields,
    }

    print(json.dumps(record, separators=(",", ":"), default=str), flush=True)


def should_log_path(path):
    if LOG_PROBES:
        return True

    return path not in {"/health", "/metrics"}


@app.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path
    ).inc()


@app.after_request
def after_request(response):
    response.headers["X-Request-ID"] = g.get("request_id", "unknown")

    if should_log_path(request.path):
        duration_ms = round((time.time() - g.get("start_time", time.time())) * 1000, 2)

        log_json(
            level="info",
            event="http_request",
            request_id=g.get("request_id", "unknown"),
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
            remote_addr=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=request.headers.get("User-Agent", ""),
        )

    return response


@app.teardown_request
def teardown_request(exception):
    if exception is None:
        return

    status = 500
    if isinstance(exception, HTTPException):
        status = exception.code

    log_json(
        level="error",
        event="request_exception",
        request_id=g.get("request_id", "unknown"),
        method=request.method,
        path=request.path,
        status=status,
        error_type=type(exception).__name__,
        error=str(exception),
    )


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


def check_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor()
    cur.execute("SELECT version();")

    version = cur.fetchone()

    cur.close()
    conn.close()

    return version


@app.route("/")
def home():
    visits = redis_client.incr("visits")
    return f"backend ok - visits: {visits}"


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")


@app.route("/db")
def db():
    version = check_db()
    return f"Postgres version: {version}"


@app.route("/health")
def health():
    return "healthy"


if __name__ == "__main__":
    log_json(
        level="info",
        event="service_starting",
        port=5000,
    )
    app.run(host="0.0.0.0", port=5000)
