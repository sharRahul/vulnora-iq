FROM python:3.12-slim

LABEL org.opencontainers.image.title="VulnoraIQ" \
      org.opencontainers.image.source="https://github.com/sharRahul/vulnoraiq" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VULNORAIQ_CONFIG_DIR=/app/config \
    VULNORAIQ_DATA_DIR=/data \
    VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports \
    VULNORAIQ_JOB_STORE_PATH=/data/jobs.db \
    VULNORAIQ_EVIDENCE_DIR=/data/evidence \
    VULNORAIQ_AUDIT_DIR=/data/audit \
    VULNORAIQ_TARGET_CONFIG=targets.docker.yaml

WORKDIR /app
RUN groupadd --system vulnoraiq && useradd --system --gid vulnoraiq --home-dir /app --shell /usr/sbin/nologin vulnoraiq
COPY requirements.txt pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .[dev]
COPY . .
RUN mkdir -p /data/reports /data/evidence /data/audit && chown -R vulnoraiq:vulnoraiq /data /app
USER vulnoraiq
VOLUME ["/data"]
EXPOSE 8787
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import http.client; c=http.client.HTTPConnection('127.0.0.1',8787,timeout=3); c.request('GET','/healthz'); r=c.getresponse(); raise SystemExit(0 if r.status < 500 else 1)"
CMD ["vulnoraiq-web", "--host", "0.0.0.0", "--port", "8787"]
