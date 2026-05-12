from flask import Flask
from prometheus_client import Counter, generate_latest
from flask import Response, request
import psycopg2
import redis
import time 
import os

time.sleep(20)

app = Flask(__name__)


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

@app.before_request
def count_request():
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path
    ).inc()


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
    app.run(host="0.0.0.0", port=5000)
