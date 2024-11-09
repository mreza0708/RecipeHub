FROM python:3.9-alpine

LABEL maintainer="londonappdeveloper.com"

ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies
RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps gcc musl-dev postgresql-dev build-base zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
      /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    -D django-user && \
mkdir -p /vol/web/media && \
mkdir -p /vol/web/static && \
chown -R django-user:django-user /vol && \
chmod -R 755 /vol




ENV PATH="/py/bin:$PATH"
USER django-user
