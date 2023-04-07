FROM ubuntu:22.04 as base

ENV DEBIAN_FRONTEND noninteractive

COPY h42backup /h42backup

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /h42backup wheels


FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

COPY h42backup /h42backup

COPY --from=base /opt/wheels /opt/wheels

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /h42backup setup

CMD ["/h42backup/h42-backup-agent"]