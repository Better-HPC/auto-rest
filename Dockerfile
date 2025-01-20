FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /build
RUN pip install /build && rm -rf /build

ENTRYPOINT ["auto-rest"]
