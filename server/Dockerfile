FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

COPY app /app

RUN apt-get update -y && apt-get install -y --no-install-recommends make && make -C /app

EXPOSE 22
EXPOSE 8000

CMD ["/app/sshd-run"]