FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV PORT=8000
ENV GRPC_PORT=50052

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# First, copy the application code
COPY ./app ${APP_HOME}/app
COPY ./models ${APP_HOME}/models

# Create proto directory
RUN mkdir -p ${APP_HOME}/proto

# Copy proto definition
COPY ./proto/valmiki.proto ${APP_HOME}/proto/

# Generate Python code from the proto file
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=app \
    --grpc_python_out=app \
    proto/valmiki.proto

# Fix imports in generated files
RUN sed -i 's/import valmiki_pb2/from . import valmiki_pb2/' app/valmiki_pb2_grpc.py

# Make sure the directory has the correct permissions
RUN chmod -R 755 ${APP_HOME}

# Create an empty __init__.py file to make the app directory a proper package
RUN touch ${APP_HOME}/app/__init__.py

# Expose both REST API and gRPC ports
EXPOSE ${PORT}
EXPOSE ${GRPC_PORT}

# Use 0.0.0.0 to make it accessible from outside the container
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
