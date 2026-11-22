FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir grpcio==1.68.1 grpcio-tools==1.68.1
COPY proto/ proto/
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/armazem.proto
COPY client/client.py .
CMD ["python", "-u", "client.py"]
