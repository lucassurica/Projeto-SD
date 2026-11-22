FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir requests==2.32.3
COPY client/client.py .
CMD ["python", "-u", "client.py"]
