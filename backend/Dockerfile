FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /workspace

RUN apk add --no-cache \
        gcc g++ musl-dev postgresql-dev libffi-dev \
        gdk-pixbuf-dev shared-mime-info gobject-introspection-dev \
        mesa-dev geos-dev curl bash sqlite \
    && rm -rf /var/cache/apk/*

RUN adduser -D -u 1000 appuser
RUN mkdir -p /workspace/logs /workspace/migrations/versions && \
    chown -R appuser:appuser /workspace

COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN uv sync --frozen --no-dev && \
    chown -R appuser:appuser /workspace/.venv

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

USER appuser

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]