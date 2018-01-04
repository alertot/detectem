FROM python:3.6.2-alpine3.6

RUN apk add --update build-base libxml2-dev libxslt-dev

RUN pip install detectem

USER nobody

ENTRYPOINT ["det"]
