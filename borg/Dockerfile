FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

COPY app /app

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app wheels



FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

COPY app /app

COPY --from=base /opt/wheels /opt/wheels

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app setup && rm -rf /app/Makefile

HEALTHCHECK CMD curl -f http://localhost/health

CMD ["fastapi", "run", "/app/main.py", "--proxy-headers", "--port", "80", "--workers", "4"]
