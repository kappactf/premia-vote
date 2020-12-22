FROM alpine

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache-dir --upgrade pip setuptools && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps build-base musl-dev python3-dev postgresql-dev linux-headers libffi-dev openssl-dev gcc libc-dev

COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt && \
    apk del .build-deps

VOLUME ["/app"]

WORKDIR /app
CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:80", "app:app"]
