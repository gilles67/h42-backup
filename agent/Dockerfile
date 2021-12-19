FROM debian

ENV DEBIAN_FRONTEND noninteractive

COPY h42backup /h42backup

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /h42backup

CMD ["/h42backup/h42-backup-agent"]