FROM ubuntu:22.04 as base

ENV DEBIAN_FRONTEND noninteractive

COPY app /app

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app wheels



FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

COPY app /app

COPY --from=base /opt/wheels /opt/wheels

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app setup

EXPOSE 22
EXPOSE 8000

CMD ["/app/sshd-run"]