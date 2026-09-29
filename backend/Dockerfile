FROM python:3.12-slim
WORKDIR /app
COPY mars_reason.py onesys.py serve.py knowledge.py packages.py catalog.json ./
RUN mkdir -p /data
ENV DATA_DIR=/data
ENV APP_ENV=production
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["python3", "serve.py"]
