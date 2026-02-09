FROM python:3.11-alpine AS build

WORKDIR /build
COPY . .

# Install build dependencies and compile source
RUN apk add --no-cache gcc libffi-dev musl-dev python3-dev
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /wheels /wheels

RUN pip install --no-compile --no-cache-dir /wheels/* && rm -rf /wheels

ENTRYPOINT ["auto-rest"]
