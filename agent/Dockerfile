FROM debian

ENV DEBIAN_FRONTEND noninteractive

COPY app /app

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app

CMD ["/app/h42-backup-agent"]