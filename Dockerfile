FROM python:3.14.7-slim-bookworm@sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f AS base

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
