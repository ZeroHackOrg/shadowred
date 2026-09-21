FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /opt/shadowred

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src

RUN pip install --no-cache-dir -e .

EXPOSE 9595

ENTRYPOINT ["sred"]
CMD ["web"]