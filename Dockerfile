FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fail2ban \
        geoip-bin \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 f2b && \
    adduser --system --uid 1001 --ingroup f2b --home /app f2b

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY f2b_core.py web_app.py ./
COPY templates/ templates/
COPY static/ static/

RUN chown -R f2b:f2b /app

USER f2b

EXPOSE 8080

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8080"]
