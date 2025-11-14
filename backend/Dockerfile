FROM python:3.13-alpine

WORKDIR /workspace

RUN apk add --no-cache \
        gcc g++ musl-dev postgresql-dev libffi-dev \
        gdk-pixbuf-dev shared-mime-info gobject-introspection-dev \
        mesa-dev geos-dev curl bash \
    && rm -rf /var/cache/apk/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

RUN adduser -D -u 1000 appuser
RUN mkdir -p /workspace/logs && \
    chown -R appuser:appuser /workspace

COPY pyproject.toml uv.lock README.md ./
RUN uv pip install --system --no-cache --prerelease=allow .

COPY . .

USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]
