FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1 # Prevents python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1      # Prevents python from buffering stdout/stderr
ENV APP_HOME=/app
ENV PORT=8000               

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app ${APP_HOME}/app
COPY ./models ${APP_HOME}/models

EXPOSE ${PORT}

# Use 0.0.0.0 to make it accessible from outside the container
# The number of workers can be adjusted based on CPU cores available
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
