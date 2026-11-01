FROM python:3.15.0-slim-bookworm@sha256:0e019bbdfb5d9874cb2389f1c2884b64aa2ac97c99960b5bc521cef978c0617d AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /discordbot
COPY requirements.txt ./
RUN python -m pip install --require-hashes -r requirements.txt
COPY src ./src

FROM base AS test
WORKDIR /discordbot
COPY requirements-dev.txt ./
RUN python -m pip install --require-hashes -r requirements-dev.txt
COPY tests ./tests
COPY pyproject.toml ./pyproject.toml
CMD ["pytest", "-q"]

FROM base AS runtime
RUN groupadd --system --gid 10001 discordbot \
    && useradd --system --uid 10001 --gid discordbot --home-dir /discordbot discordbot
USER discordbot
CMD ["python3", "src/main.py"]
