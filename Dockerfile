FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="VulnoraIQ" \
      org.opencontainers.image.description="AI security assessment framework for LLM applications, RAG systems, agents, and orchestration layers" \
      org.opencontainers.image.source="https://github.com/sharRahul/vulnoraiq" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="0.2.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VULNORAIQ_HOST=0.0.0.0 \
    VULNORAIQ_PORT=8787 \
    VULNORAIQ_JOB_STORE_BACKEND=sqlite \
    VULNORAIQ_JOB_STORE_PATH=/data/jobs.db \
    VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports \
    VULNORAIQ_AUTH_ENABLED=true \
    VULNORAIQ_ENV=production

WORKDIR /app

RUN addgroup --system --gid 1001 vulnoraiq && \
    adduser --system --uid 1001 --gid 1001 --no-create-home vulnoraiq

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e . --no-cache-dir && \
    rm -rf /root/.cache/pip

COPY agent_testing ./agent_testing
COPY benchmarks ./benchmarks
COPY config ./config
COPY core ./core
COPY dashboards ./dashboards
COPY examples ./examples
COPY integrations ./integrations
COPY modules ./modules
COPY payloads ./payloads
COPY rag_testing ./rag_testing
COPY reports ./reports
COPY scripts ./scripts
COPY webui ./webui

RUN chown -R vulnoraiq:vulnoraiq /app && \
    mkdir -p /data && \
    chown vulnoraiq:vulnoraiq /data

USER vulnoraiq

VOLUME ["/data"]

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/healthz', timeout=3).read()"

CMD ["sh", "-c", "vulnoraiq-web --host ${VULNORAIQ_HOST} --port ${VULNORAIQ_PORT}"]
