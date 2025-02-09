FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY todoical.py /app

ENTRYPOINT ["python3"]
CMD ["app.py"]
