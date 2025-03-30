# Valmiki Microservice

This microservice provides a REST API endpoint to predict the age group and gender of a person from an uploaded image. It uses FastAPI, OpenCV's DNN module, and pre-trained Caffe models (AgeNet, GenderNet, Face Detector). The service is optimized for CPU-only deployment and aims for low latency.

## Features

* **FastAPI Framework**: High-performance asynchronous web framework.
* **OpenCV DNN**: Loads and runs Caffe models for inference.
* **Face Detection**: Uses an SSD-based face detector to locate the face before prediction (robust to imperfect images).
* **Age Prediction**: Classifies age into predefined buckets (e.g., '(25-32)').
* **Gender Prediction**: Classifies gender as 'Male' or 'Female'.
* **CPU Optimized**: Designed to run efficiently on CPU.
* **Dockerized**: Includes a Dockerfile for easy containerization and deployment (e.g., on AWS).

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone git@github.com:ADVERIE/valmiki.git
    cd valmiki
    ```

2.  **Download Models:**
    * Download the required `.prototxt` and `.caffemodel` files for the face detector, AgeNet, and GenderNet. See links in the "Model Files Acquisition" section of the thought process or source code comments (`app/predictor.py`).
    * Place all downloaded model files into the `models/` directory within the project root. The expected structure is:
        ```
        models/
        ├── deploy.prototxt
        ├── res10_300x300_ssd_iter_140000.caffemodel
        ├── age_deploy.prototxt
        ├── age_net.caffemodel
        ├── gender_deploy.prototxt
        └── gender_net.caffemodel
        ```

3.  **Build the Docker Image:**
    ```bash
    docker build -t valmiki .
    ```

## Running the Service

1.  **Run the Docker Container:**
    ```bash
    docker run -p 8000:8000 --name valmiki valmiki
    ```
    * `-p 8000:8000`: Maps port 8000 on your host machine to port 8000 inside the container.
    * `--name valmiki`: Assigns a name to the running container for easier management.
    * You can override the port using the `-e` flag: `docker run -p 8080:8080 -e PORT=8080 --name valmiki valmiki`

## API Endpoints

The service will be available at `http://localhost:8000` (or the host port you mapped).

* **Health Check:**
    * **URL:** `/health`
    * **Method:** `GET`
    * **Success Response (200 OK):**
        ```json
        {
          "status": "OK"
        }
        ```
    * **Failure Response (503 Service Unavailable - if models failed to load):**
        ```json
        {
            "status": "error",
            "detail": "Models not loaded"
        }
        ```

* **Predict Age and Gender:**
    * **URL:** `/predict`
    * **Method:** `POST`
    * **Body:** `multipart/form-data` with a single field named `file` containing the image data.
    * **Success Response (200 OK):**
        ```json
        {
          "age": "(25-32)",  // Example age bucket
          "gender": "Male"  // Example gender
        }
        ```
    * **Error Responses:**
        * `400 Bad Request`: If the file is invalid, empty, or no face is detected.
            ```json
            {
              "detail": "No face detected"
            }
            ```
        * `500 Internal Server Error`: If there's an issue during image processing or model inference.
            ```json
            {
              "detail": "OpenCV processing error: <specific error>"
            }
            ```
        * `503 Service Unavailable`: If the models failed to load on startup.
            ```json
            {
                "detail": "Models are not loaded, service cannot process requests."
            }
            ```

## Testing with cURL

1.  **Health Check:**
    ```bash
    curl http://localhost:8000/health
    ```

2.  **Prediction:** (Replace `path/to/your/image.jpg` with an actual image file path)
    ```bash
    curl -X POST -F "file=@path/to/your/image.jpg" http://localhost:8000/predict
    ```

## Configuration (Environment Variables)

* `PORT`: The port number the Uvicorn server inside the container listens on. Defaults to `8000`. Can be set during `docker run` using the `-e PORT=<desired_port>` flag (remember to map the host port accordingly with `-p`). Model paths are currently hardcoded relative to the `predictor.py` file but could be made configurable via environment variables if needed.

## Deployment on AWS

1.  **Build the Docker Image:** As described above.
2.  **Push to a Registry:** Push the image to a container registry like Amazon ECR (Elastic Container Registry).
3.  **Deploy:** Deploy the container using AWS services like:
    * **Amazon ECS (Elastic Container Service):** A managed container orchestration service. Define a Task Definition pointing to your ECR image and run it as a Service or Task.
    * **AWS App Runner:** A simpler service for deploying containerized web applications directly from a registry.
    * **Amazon EKS (Elastic Kubernetes Service):** If you prefer Kubernetes.
    * **EC2 Instance:** Run the Docker container directly on an EC2 instance (requires managing the instance and Docker daemon).

Ensure security groups and network configurations allow traffic to the port your container exposes (e.g., port 8000).

## Code Organization

* `app/main.py`: FastAPI application setup, routes (`/health`, `/predict`), request/response handling.
* `app/predictor.py`: Core logic for loading models, image preprocessing (including face detection), running inference with OpenCV DNN, and formatting results. Models are loaded once on module import.
* `models/`: Stores the Caffe model files.
* `Dockerfile`: Defines the container build process.
* `requirements.txt`: Lists Python dependencies.
