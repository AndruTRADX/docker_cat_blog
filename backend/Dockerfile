FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app

COPY --from=builder /root/.local /home/nonroot/.local
COPY . .

ENV PATH=/home/nonroot/.local/bin:$PATH
ENV PYTHONPATH=/home/nonroot/.local/lib/python3.11/site-packages

CMD ["app.py"] 
