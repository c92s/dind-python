FROM docker:28.0.4-dind-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update --quiet && apk upgrade --quiet
RUN apk add --no-cache --quiet \
    python3=3.12.9-r0 \
    python3-dev=3.12.9-r0 \
    py3-pip==24.3.1-r0
